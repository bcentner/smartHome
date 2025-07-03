"""
Facial Recognition Module for SmartHome System
Handles real-time face detection and recognition.
"""

import logging
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import threading
from typing import Optional, Dict, Any

from error_handler import (
    FacialRecognitionError, CameraError, handle_errors, safe_execute
)


class FaceRecognition:
	"""Facial recognition system for user identification."""
	
	def __init__(self, config) -> None:
		self.config = config
		self.logger = logging.getLogger(__name__)
		self._new_person_found = False
		self._person = ""
		self._lock = threading.Lock()
		self.running = False
		self.thread = threading.Thread(target=self.run)
		self.vs: Optional[VideoStream] = None
		self.fps: Optional[FPS] = None
		
	def start(self):
		"""Start the facial recognition system."""
		try:
			self.logger.info("Starting face recognition")
			self.running = True
			self.thread.start()
		except Exception as e:
			raise FacialRecognitionError(f"Failed to start facial recognition: {str(e)}")

	def stop(self):
		"""Stop the facial recognition system."""
		try:
			self.logger.info("Stopping face recognition")
			self.running = False
			if self.thread.is_alive():
				self.thread.join(timeout=5)
			if self.vs:
				self.vs.stop()
			if self.fps:
				self.fps.stop()
			cv2.destroyAllWindows()
		except Exception as e:
			self.logger.error(f"Error stopping facial recognition: {e}")

	@property
	def new_person_found(self) -> bool:
		with self._lock:
			return self._new_person_found
	
	@property
	def get_name(self) -> str:
		with self._lock:
			return self._person
		
	def reset_new_person_found(self) -> None:
		with self._lock:
			self._new_person_found = False

	def run(self):
		"""Main facial recognition processing loop."""
		try:
			# Initialize 'currentname' to trigger only when a new person is identified.
			currentname = "unknown"
			
			# Get encodings file path from configuration
			encodings_file = self.config.get('facial_recognition.encodings_file', 'encodings.pickle')
			
			# Load the known faces and embeddings
			self.logger.info("Loading encodings and face detector...")
			try:
				with open(encodings_file, "rb") as f:
					data = pickle.loads(f.read())
			except FileNotFoundError:
				raise FacialRecognitionError(f"Encodings file not found: {encodings_file}")
			except Exception as e:
				raise FacialRecognitionError(f"Failed to load encodings: {str(e)}")

			# Get camera settings from configuration
			camera_settings = self.config.get_camera_settings()
			
			# Initialize the video stream
			try:
				self.vs = VideoStream(
					src=camera_settings['source'],
					framerate=camera_settings['framerate']
				).start()
				time.sleep(2.0)  # Allow camera sensor to warm up
			except Exception as e:
				raise CameraError(f"Failed to initialize camera: {str(e)}")

			# Start the FPS counter
			self.fps = FPS().start()

			# Main processing loop
			while self.running:
				try:
					# Grab the frame from the threaded video stream and resize it
					# to 500px (to speedup processing)
					frame = self.vs.read()
					if frame is None:
						self.logger.warning("Failed to read frame from camera")
						continue
						
					frame = imutils.resize(frame, width=camera_settings['width'])
					
					# Detect the face boxes
					boxes = face_recognition.face_locations(frame)
					# Compute the facial embeddings for each face bounding box
					encodings = face_recognition.face_encodings(frame, boxes)
					names = []

					# Loop over the facial embeddings
					for encoding in encodings:
						# Attempt to match each face in the input image to our known encodings
						matches = face_recognition.compare_faces(
							data["encodings"], encoding, 
							tolerance=self.config.get('facial_recognition.tolerance', 0.6)
						)
						name = "Unknown"  # If face is not recognized, then print Unknown

						# Check to see if we have found a match
						if True in matches:
							# Find the indexes of all matched faces then initialize a
							# dictionary to count the total number of times each face was matched
							matchedIdxs = [i for (i, b) in enumerate(matches) if b]
							counts = {}

							# Loop over the matched indexes and maintain a count for
							# each recognized face
							for i in matchedIdxs:
								name = data["names"][i]
								counts[name] = counts.get(name, 0) + 1

							# Determine the recognized face with the largest number
							# of votes (note: in the event of an unlikely tie Python
							# will select first entry in the dictionary)
							name = max(counts, key=counts.get)

							# If someone in your dataset is identified, print their name on the screen
							if currentname != name:
								currentname = name
								self.logger.info(f"Recognized {currentname}")
								with self._lock:
									self._person = currentname
									self._new_person_found = True

						# Update the list of names
						names.append(name)

					# Loop over the recognized faces
					for ((top, right, bottom, left), name) in zip(boxes, names):
						# Draw the predicted face name on the image - color is in BGR
						cv2.rectangle(frame, (left, top), (right, bottom),
							(0, 255, 225), 2)
						y = top - 15 if top - 15 > 15 else top + 15
						cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
							.8, (0, 255, 255), 2)

					# Display the image to our screen
					cv2.imshow("Facial Recognition is Running", frame)
					key = cv2.waitKey(1) & 0xFF

					# Quit when 'q' key is pressed
					if key == ord("q"):
						self.running = False
						break

					# Update the FPS counter
					self.fps.update()
					
				except Exception as e:
					self.logger.error(f"Error processing frame: {e}")
					continue

		except Exception as e:
			self.logger.error(f"Fatal error in facial recognition: {e}")
			raise FacialRecognitionError(f"Facial recognition failed: {str(e)}")
		finally:
			# Stop the timer and display FPS information
			if self.fps:
				self.fps.stop()
				self.logger.info(f"Elapsed time: {self.fps.elapsed():.2f}")
				self.logger.info(f"Approx. FPS: {self.fps.fps():.2f}")

			# Do a bit of cleanup
			cv2.destroyAllWindows()
			if self.vs:
				self.vs.stop()
