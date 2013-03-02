"""
This file is part of opensesame.

opensesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

opensesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with opensesame.  If not, see <http://www.gnu.org/licenses/>.
"""


from libopensesame import item, exceptions
from libqtopensesame import qtplugin
from openexp.canvas import canvas
from openexp.mouse import mouse
import os.path
import math
import sys
from PyQt4 import QtGui, QtCore


class slider(item.item):

	"""Basic functionality of the plug-in"""

	def __init__(self, name, experiment, string = None):

		"""
		Constructor

		Arguments:
		name -- name of the item
		experiment -- the experiment

		Keyword arguments:
		string -- definitional string (default = None)
		"""

		global path		

		self.item_type = "slider"
		self.description = "Presents a question and slider"

		self._question = "Put your question here"
		self._accept_text = "Click to accept"
		self.slider_w = 800
		self.slider_h = 10
		self.txt_colour = 'white'
		self.sf_colour = 'red'
		self.fg_colour = 'white'
		self.bg_colour = 'black'

		# Pass the word on to the parent
		item.item.__init__(self, name, experiment, string)

	def prepare(self):

		"""Prepare the item"""

		# Slider dimensions
		self.slider_x = self.get("width")/2-self.slider_w/2
		self.slider_y = self.get("height")/2-self.slider_h/2

		# background colour
		self.canvas = canvas(self.experiment)
		self.canvas.set_bgcolor(self.get("bg_colour"))
		self.canvas.clear()

		# Draw the text 
		self.canvas.text(self.get("_question"), y=self.slider_y-100, color=self.get("txt_colour"))
		self.canvas.text(self.get("_accept_text"), y=self.slider_y+self.slider_h+50, color=self.get("txt_colour"))

		# Draw the slider frame
		self.canvas.set_fgcolor(self.get("fg_colour"))
		self.canvas.rect(self.slider_x-1, self.slider_y-1, self.slider_w+2, self.slider_h+2)

		# Pass the word on to the parent
		item.item.prepare(self)

		#generic_response.generic_response.prepare(self)
		return True
		
	def run(self):

		"""Run the item"""

		# Initialize the item
		self.set_item_onset()
		self.sri = self.time()
		self.experiment.set("slider_percent", None)
		slmouse = mouse(self.experiment, timeout=20)

		# Run slider
		while True:
			
			# Determine the slider fill based on the mouse position
			pos, time = slmouse.get_pos()
			x, y = pos
			slider_fill = min(self.slider_w, max(0, x-self.slider_x))

			# Draw the slider fill
			self.canvas.rect(self.slider_x, self.slider_y, slider_fill, self.slider_h, fill=True, color=self.get("sf_colour"))

			# Draw the canvas
			self.canvas.show()

			# Reset slider fill
			self.canvas.rect(self.slider_x, self.slider_y, slider_fill, self.slider_h, fill=True, color=self.get("bg_colour"))

			# Poll the mouse for buttonclicks
			button, position, timestamp = slmouse.get_click(timeout = 1)
			if button != None:
				break

		slider_percent = round(100.0 * (float(slider_fill)/float(self.slider_w)),2)

		# Set the response and response time
		self.experiment.set("response", slider_percent)

		# Return success
		return True

class qtslider(slider, qtplugin.qtplugin):

	"""The GUI aspect of the plugin"""

	def __init__(self, name, experiment, string = None):

		"""
		Constructor

		Arguments:
		name -- name of the item
		experiment -- the experiment

		Keyword arguments:
		string -- definitional string (default = None)
		"""

		# Pass the word on to the parents
		slider.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):

		"""Build the edit controls"""

		self.lock = True

		# Pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)

		# Content editor
		self.add_spinbox_control("slider_width", "Slider width", 10, 1000, tooltip = "The width of the text area")
		self.add_spinbox_control("slider_heigth", "Slider height", 0, 100, tooltip = "The height of the text area")		
		self.add_color_edit_control("txt_colour", "Text colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("fg_colour", "Foreground colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("sf_colour", "Slider filling colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_color_edit_control("bg_colour", "Background colour", tooltip = "Expecting a colorname (e.g., 'blue') or an HTML color (e.g., '#0000FF')")
		self.add_line_edit_control("_accept_text", "Text underneath the slider", tooltip = "The text that appears below slider")
		self.add_editor_control("_question", "Question", tooltip = "The question that you want to ask")

		self.lock = False

	def apply_edit_changes(self):

		"""Apply changes to the controls"""

		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return
		self.experiment.main_window.refresh(self.name)

	def edit_widget(self):

		"""Refresh the controls"""

		self.lock = True
		qtplugin.qtplugin.edit_widget(self)
		self.lock = False
		return self._edit_widget

