"""
Authors: Sujeendra, Rammesh, Nikil
importing the required module
"""

import sys
import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from nav_msgs.msg import Odometry
import math
from tf.transformations import euler_from_quaternion
from guidance import models, gen, system, user, assistant
import guidance
import os
import json
import csv
import time


"""
llm class for interacting with gpt api and get the desired response

"""
class llm:

    def __init__(self):
        os.environ['OPENAI_API_KEY'] = ' '
        self.end = None
        self.model = models.OpenAI("gpt-3.5-turbo")
        self.llm_chain = self.model

    def init_llm(self):
        with system():
            #chain of thought prompting technique
            self.llm_chain += f"""\
                You need to serve as a robot that takes input from the user which can contain shapes which a drone needs to follow. Your purpose is to give certain coordinates as output which will be implemented on the drone, the rubrics for the output coordinates will be mentioned below.

                Rubrics:
                
                coordinate_system:
                The below mentioned is the coordinate system of the drone:
                One coordinate is in the format [x,y,z]
                left: increasing x makes the drone moves left - for example current position = [0,0,0] change it to [5,0,0] makes robot move left by 5 units 
                right: decreasing x makes the drone moves right - for example current position = [0,0,0] change it to [-5,0,0] makes robot move right by 5 units 
                backward: increasing y makes the drone moves backward - for example current position = [0,0,0] change it to [0,5,0] makes robot move backward by 5 units 
                forward: decreasing y makes the drone moves forward - for example current position = [0,0,0] change it to [0,-5,0] makes robot move forward by 5 units
                up: increasing z makes the drone moves up - for example current position = [0,0,0] change it to [0,0,5] makes robot move up by 5 units
                down: decreasing z makes the drone moves down- for example current position = [0,0,5] change it to [0,0,0] makes robot move down by 5 units

                operation_list:
                square
                directions
                combination

                Guidlines:
                Read and understand the coordinate_system well before going to operations. Keep it as the base to perform any right, left, forward, backward, up or down operation
                If the height at which the drone has to fly is not mentioned then take it default as 5 meters 
                When it is the end of the operation wait for next response from user
                If user command contains key words linke box or rectangle or square or any synonyms relatedto this it belongs to square in operation_list
                If user command contains anything like go straight take left or right or anything similar to this fashion then it comes under directions in operation_list
                If the user command consists of anything which you feel is a combination of directions and square then it comes under combination.
                
                When you finalize an operation from operation_list follow the instruction from the Operations given below,make sure to match the Operation_implement to be the same as operation_list and then follow the respective instructions
                If the user mentions anything that's not from operation_list try to find the closest synonym of word from the operation_list, or else send a output which says "command not understood, please make it more clear"
                

                
                Operations:


                Operation_implement: "square"
                If the user mentions about a square or rectangle of some particular units or length and width or area.
                
                Square_operation_default_value:
                If the user dosen't mention any units then take default as 5 units
                
                Example-1 for "square":
                input: square of 5 units
                output:
                [0,0,5]
                [0,-5,5] 
                [-5,-5,5] 
                [-5,0,5] 
                [0,0,5] 
                Explanation:
                First the drone initial position will be [0,0,0]. Since the height is not mentioned take the default height mentioned in Guidlines, so we need to make it go up by 5 units, so we increase the z by 5 units according to coordinate_system to go up. this generates the first line [0,0,5]
                After this we need to make it go forward for 5 meters at the same height so in addition to the first line which is [0,0,5] we change the y coordinate by decreasing it by 5 units according to coordinate_system to [0,-5,5], this will be the second line of output
                After this we need to make it go right for 5 meters at the same height so in addition to the second line which is [0,-5,5] we change the x coordinate by decreasing it by 5 units according to coordinate_system to [-5,-5,5], this will be the third line of output
                After this we need to make it go backward for 5 meters at the same height so in addition to the third line which is [-5,-5,5] we change the y coordinate by increasing it by 5 units according to coordinate_system to [-5,0,5], this will be the fourth line of output
                After this we need to make it go left for 5 meters at the same height so in addition to the fourth line which is [-5,0,5] we change the x coordinate by increasing it by 5 units according to coordinate_system to [0,0,5], this will be the fifth line of output 


                Operation_implement: "directions"
                If the user mentions about going forward or straight or up or left or right which usually resembles directions
                Make sure to go through directions_operation_default_value

                "home_location" = [0,0,5]
                
                directions_operation_default_value:
                If the user dosen't mention any units then take default as 5 units
                User might give multiple insturctions make sure to understand it properly and segment them and generate coordinates.
                Mostly words like "and" and "," separates the input into segments
                When the operation is "directions" always end the output with home_location
                
                Example-1 for "directions":
                input: go straight for 5 meters, take left for 10 meters, go straight for 20 meters and take right for 5 meters
                output:
                [0,0,5]
                [0,-5,5]
                [10,-5,5]
                [10,-25,5]
                [5,-25,5]
                [0,0,5]
                Explanation:
                firstly analyse the input and segment it into multiple chunks in order like:
                "go straight for 5 meters" - first segment
                "take left for 10 meters" - second segment
                "go straight for 20 meters" - third segment
                "take right for 5 meters" - fourth segment
                this is the order at which you need to generate coordinates
                First the drone initial position will be [0,0,0]. Since the height is not mentioned take the default height mentioned in Guidlines, so we need to make it go up by 5 units, so we increase the z by 5 units according to coordinate_system to go up. This generates the first line [0,0,5]
                In the first segment it is mentioned as "go straight for 5 meters" , so make it go forward for 5 meters at the same height so in addition to the first line which is [0,0,5] we change the y coordinate by decreasing it by 5 units according to coordinate_system to [0,-5,5], this explains the second line of the output
                In the second segment it is mentioned as "take left for 10 meters". We need to make it go left for 10 meters at the same height so in addition to the second line which is [0,-5,5] we change the x coordinate by increasing it by 10 units according to coordinate_system to [10,-5,5], this explains the third line of the output
                In the third segment it is mentioned as "go straight for 20 meters". We need to make it go forward for 20 meters at the same height so in addition to the third line which is [10,-5,5] we change the y coordinate by decreasing it by 20 units according to coordinate_system to [10,-25,5], this explains the fourth line of the output
                In the fourth segment it is mentioned as "take right for 5 meters". We need to make it go right for 5 meters at the same height so in addition to the fourth line which is [10,-25,5] we change the x coordinate by decreasing it by 5 units according to coordinate_system to [5,-25,5], this explains the fifth line of the output
                Sixth line of the output is the "home_location" always add it in the end of an operation in "directions" operation
                
                Example-2 for "directions"
                input: go straight for 5 meters, take right for 10 meters, go straight for 20 meters and take left for 5 meters
                output:
                [0,0,5]
                [0,-5,5]
                [-10,-5,5]
                [-10,-25,5]
                [-5,-25,5]
                [0,0,5]
                Explanation: 
                firstly analyse the input and segment it into multiple chunks in order like:
                "go straight for 5 meters" - first segment
                "take right for 10 meters" - second segment
                "go straight for 20 meters" - third segment
                "take left for 5 meters" - fourth segment
                this is the order at which you need to generate coordinates
                First the drone initial position will be [0,0,0]. Since the height is not mentioned take the default height mentioned in Guidlines, so we need to make it go up by 5 units, so we increase the z by 5 units according to coordinate_system to go up. This generates the first line [0,0,5]
                In the first segment it is mentioned as "go straight for 5 meters" , so make it go forward for 5 meters at the same height so in addition to the previous line of output which is the first line that is [0,0,5] we change the y coordinate by decreasing it by 5 units according to coordinate_system to [0,-5,5], this explains the second line of the output
                In the second segment it is mentioned as "take right for 10 meters". We need to make it go right for 10 meters at the same height so in addition to the previous line of output which is the second line that is [0,-5,5] we change the x coordinate by decreasing it by 10 units according to coordinate_system to [-10,-5,5], this explains the third line of the output
                In the third segment it is mentioned as "go straight for 20 meters". We need to make it go forward for 20 meters at the same height so in addition to the previous line of output which is the third line that is [-10,-5,5] we change the y coordinate by decreasing it by 20 units according to coordinate_system to [-10,-25,5], this explains the fourth line of the output
                In the fourth segment it is mentioned as "take left for 5 meters". We need to make it go left for 5 meters at the same height so in addition to the previous line of output which is the fourth line that is [-10,-25,5] we change the x coordinate by increasing it by 5 units according to coordinate_system to [-5,-25,5], this explains the fifth line of the output
                Sixth line of the output is the "home_location" always add it in the end of an operation in "directions" operation

                Example-3 for "directions"
                input: left, right, back
                output:
                [0,0,5]
                [5,0,5]
                [0,0,5]
                [0,5,5]
                [0,0,5]
                Explanation:
                Since the left, right, back distance is not mentioned take the default left, right, back values mentioned in directions_operation_default_value 
                firstly analyse the input and segment it into multiple chunks in order like:
                "left" - first segment
                "right" - second segment
                "back" - third segment
                this is the order at which you need to generate coordinates
                First the drone initial position will be [0,0,0]. Since the height is not mentioned take the default height mentioned in Guidlines, so we need to make it go up by 5 units, so we increase the z by 5 units according to coordinate_system to go up. This generates the first line [0,0,5]
                In the first segment it is mentioned as "left" , so make it go left for 5 meters at the same height so in addition to the previous line of output which is the first line that is [0,0,5] we change the x coordinate by increasing it by 5 units according to coordinate_system to [5,0,5], this explains the second line of the output
                In the second segment it is mentioned as "right". We need to make it go right for 5 meters at the same height so in addition to the previous line of output which is the second line that is [5,0,5] we change the x coordinate by decreasing it by 5 units according to coordinate_system to [0,0,5], this explains the third line of the output
                In the third segment it is mentioned as "back". We need to make it go backward for 5 meters at the same height so in addition to the previous line of output which is the third line that is [0,0,5] we change the y coordinate by increasing it by 5 units according to coordinate_system to [0,5,5], this explains the fourth line of the output
                Fifth line of the output is the "home_location" always add it in the end of an operation in "directions" operation

                Example-4 for "directions"
                input: left at height 10
                output:
                [0,0,10]
                [5,0,10]
                [0,0,5]

                Example-5 for "directions"
                input: got at height 20 and go left for 20 meters and then go straight for 30 meters and then take right
                output:
                [0,0,20]
                [20,0,20]
                [20,-30,20]
                [15,-30,20]
                [0,0,5]
                Explanation:
                Since the right distance is not mentioned take the default right values mentioned in directions_operation_default_value
                firstly analyse the input and segment it into multiple chunks in order like:
                "got at height 20" - first segment
                "and" - spearates first and second segment
                "go left for 20 meters" - second segment
                "and" - spearates second and third segment
                "then go straight for 30 meters" - third segment
                "and" - spearates third and fourth segment
                "then take right" - fourth segment
                this is the order at which you need to generate coordinates
                In the first segment it is mentioned as "got at height 20". It means go up for 20 meters from initial position which is [0,0,0] we change the z coordinate by increasing it by 20 units according to coordinate_system to [0,0,20], this explains the first line of the output
                In the second segment it is mentioned as "go left for 20 meters". It means go left for 20 meters at the same height so in addition to the previous line of output which is first line that is [0,0,20] we change the x coordinate by increasing it by 20 units according to coordinate_system to [20,0,20], this explains the second line of the output
                In the third segment it is mentioned as "then go straight for 30 meters". It means go forward for 30 meters at the same height so in addition to the previous line of output which is second line that is [20,0,20] we change the y coordinate by dereasing it by 20 units according to coordinate_system to [20,-30,20], this explains the third line of the output
                In the fourth segment it is mentioned as "then take right". It means go right for 5 meters at the same height so in addition to the previous line of output which is third line that is [20,-30,20] we change the x coordinate by dereasing it by 5 units according to coordinate_system to [15,-30,20], this explains the fourth line of the output
                Fifth line of the output is the "home_location" always add it in the end of an operation in "directions" operation

                Example-6 for "directions"
                input: go straight for 10, take left for 5, take right for 20, come back for 20
                input:
                [0,0,5]
                [0,-10,5]
                [5,-10,5]
                [-15,-10,5]
                [-15,10,5]
                [0,0,5]
                Explanation:
                firstly analyse the input and segment it into multiple chunks in order like:
                "go straight for 10" - first segment
                "," - spearates first and second segment
                "take left for 5" - second segment
                "," - spearates second and third segment
                "take right for 20" - third segment
                "," - spearates third and fourth segment
                "come back for 20" - fourth segment
                this is the order at which you need to generate coordinates
                First the drone initial position will be [0,0,0]. Since the height is not mentioned take the default height mentioned in Guidlines, so we need to make it go up by 5 units, so we increase the z by 5 units according to coordinate_system to go up. This generates the first line [0,0,5]
                In the first segment it is mentioned as "go straight for 10 meters". It means go forward for 10 meters at the same height so in addition to the previous line of output which is first line that is [0,0,5] we change the y coordinate by decreasing it by 10 units according to coordinate_system to [0,-10,5], this explains the second line of the output
                In the second segment it is mentioned as "take left for 5 meters". It means go left for 5 meters at the same height so in addition to the previous line of output which is second line that is [0,-10,5] we change the x coordinate by increasing it by 5 units according to coordinate_system to [5,-10,5], this explains the third line of the output
                In the third segment it is mentioned as "take right for 20 meters". It means go right for 20 meters at the same height so in addition to the previous line of output which is the third line that is [5,-10,5] we change the x coordinate by decreasing it by 20 units according to coordinate_system to [-15,-10,5], this explains the fourth line of the output
                In the fourth segment it is mentioned as "come back for 20". It means go backward for 20 meters at the same height so in addition to the previous line of output which is the  fourth line that is [-15,-10,5] we change the y coordinate by increasing it by 20 units according to coordinate_system to [-15,10,5], this explains the fifth line of the output
                Sixth line of the output is the "home_location" always add it in the end of an operation in "directions" operation

                Example-7 for "directions"
                input: right at height 10
                output:
                [0,0,10]
                [-5,0,10]
                [0,0,5]

                Example-8 for "directions"
                input: go straight and take left
                output:
                [0,0,5]
                [0,-5,5]
                [5,-5,5]
                [0,0,5]

                
                Conversation Output Format:
                The outcome of your interactions must be documented as follows, without using markdown script for responses. Please only return a json object with:
                1. "text": Waypoints deployed on the drone
                2. "coordinates": The output you have been trained to generate. The coordinates should be a list of points, where each point is a list of 3D x,y,z coordinates.

                """

    #getting result from the gpt
    def generate_response(self, prompt):
        with user():
            self.llm_chain += f"""\
                                {prompt}"""

        with assistant():
            self.llm_chain += gen(name='answer', max_tokens=500)
        
        return self.llm_chain
    

"""
Drone control class to read in all the coordinates given by llm and executes it in order
Simple controller checks for the setpoint error of 0.5 which is the eucliedien distance and then executes next coordinates

"""

class DroneControl(QWidget):
    def __init__(self):
        super().__init__()

        #ui initialisation
        self.init_ui()

        # List to store history of prompts and responses
        self.history = []

        # ROS node initialization
        rospy.init_node('drone_controller')
        #publishes setpoint to the drone
        self.publisher = rospy.Publisher('/drone1/mavros/setpoint_position/local', PoseStamped, queue_size=10)
        #reads the current position of drone in local coordinates
        self.subscriber=rospy.Subscriber('/drone1/mavros/local_position/pose',PoseStamped,self.current_position_callback)
        #this will be updated using llm

        self.setpoints=None
        self.currentposition=None

        #for now the orientation is fixed and not changed--> this will point the heading of the drone towards the user
        self.desired_orientation = Quaternion(x=0.0, y=0.0, z=0.7071, w=0.7071)
        #these are required for plotting
        self.result=[]

    def current_position_callback(self,data):
        self.currentposition=data.pose
        #required for plotting
        self.result.append([data.pose.position.x,data.pose.position.y,data.pose.position.z,time.time()])

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Drone Control')
        # Set initial size of the window
        self.resize(800, 600)  

        # Text fields for prompt, response, and history
        self.text_edit_prompt = QTextEdit()
        self.text_edit_response = QTextEdit()
        self.text_edit_response.setReadOnly(True)
        self.text_edit_history = QTextEdit()
        self.text_edit_history.setReadOnly(True)

        # Labels
        label_prompt = QLabel("Enter command:")
        label_response = QLabel("Response:")
        label_history = QLabel("History:")

        # Button to generate response
        self.button_generate = QPushButton('Generate Response')
        self.button_generate.clicked.connect(self.generate_response)

        # Button to clear history
        self.button_clear = QPushButton('Clear History')
        self.button_clear.clicked.connect(self.clear_history)

        # Button to execute controller
        self.button_execute = QPushButton('Execute Controller')
        self.button_execute.clicked.connect(self.execute_controller)

        # Apply some basic styles
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QTextEdit, QPushButton {
                font-size: 12px;
            }
        """)

        # Layout for labels
        layout_labels = QVBoxLayout()
        layout_labels.addWidget(label_prompt)
        layout_labels.addWidget(label_response)
        layout_labels.addWidget(label_history)

        # Layout for text fields
        layout_texts = QVBoxLayout()
        layout_texts.addWidget(self.text_edit_prompt)
        layout_texts.addWidget(self.text_edit_response)
        layout_texts.addWidget(self.text_edit_history)

        # Horizontal layout for text fields and labels
        layout_input_output = QHBoxLayout()
        layout_input_output.addLayout(layout_labels)
        layout_input_output.addLayout(layout_texts)

        # Vertical layout for buttons and input/output layout
        layout_controls = QVBoxLayout()
        layout_controls.addWidget(self.button_generate)
        layout_controls.addWidget(self.button_clear)
        layout_controls.addWidget(self.button_execute)
        layout_controls.addLayout(layout_input_output)

        # Main layout
        layout = QHBoxLayout()
        layout.addLayout(layout_controls)
        self.setLayout(layout)

    def generate_response(self):
        # Get the prompt text
        prompt_text = self.text_edit_prompt.toPlainText()
        gpt = llm()
        gpt.init_llm()
        json_val=gpt.generate_response(prompt_text)['answer']
        result = json.loads(json_val)
        #add only if resonse form llm is in this format otherwise something is wrong and drone will execute the previous command
        if('coordinates' in result):
            self.setpoints=result["coordinates"]
        # Generate response (replace this with your actual ChatGPT code)
        response_text = "Sample response to the command: '" + prompt_text + "\n'"
        #reading data from the llm directly the coordinates
        response_text+=str(result)
        # Update response text field
        self.text_edit_response.setPlainText(response_text)

        # Update history
        self.history.append((prompt_text, response_text))
        self.update_history()

    def clear_history(self):
        # Clear the history list and update history text field
        self.history = []
        self.update_history()

    def update_history(self):
        # Display history in the history text field
        history_text = ""
        for prompt, response in self.history:
            history_text += f"Command: {prompt}\nResponse: {response}\n\n"
        self.text_edit_history.setPlainText(history_text)

    """
    sending coordinates to the controller or publishing data over ros topic
    """
    def execute_controller(self):
        pose=PoseStamped()
        #execute set points one by one until it is reached
        #self.arm()
        #manually arm the drone and set the mode to guided to execute autonomous mission
        print("starting")
        i=1
        for point in self.setpoints:
            print("waypoint no. : ",i)
            pose.pose.position.x=point[0]
            pose.pose.position.y=point[1]
            pose.pose.position.z=point[2]

            #this is controlling orientation based on llm output but for now it is not read from llm but this is a future work.
            desired_quaternion = (self.desired_orientation.x,
                                  self.desired_orientation.y,
                                  self.desired_orientation.z,
                                  self.desired_orientation.w)

            pose.pose.orientation.x=self.desired_orientation.x
            pose.pose.orientation.y=self.desired_orientation.y
            pose.pose.orientation.z=self.desired_orientation.z
            pose.pose.orientation.w=self.desired_orientation.w

            #sending desired pose over topic
            self.publisher.publish(pose)

            #contnously check for coordinate reach 
            while True:
                #get the eucliedien distance : between desired and current position
                #the pid controller is implemented inside the mavros so we do not worry about that
                dist=math.sqrt((self.currentposition.position.x-point[0])**2+(self.currentposition.position.y-point[1])**2+(self.currentposition.position.z-point[2])**2)
                current_quaternion = (self.currentposition.orientation.x,
                        self.currentposition.orientation.y,
                        self.currentposition.orientation.z,
                        self.currentposition.orientation.w)
                (roll, pitch, yaw) = euler_from_quaternion(current_quaternion)
                (desired_roll, desired_pitch, desired_yaw) = euler_from_quaternion(desired_quaternion)

                # You can set an acceptable threshold for orientation difference
                roll_diff = abs(roll - desired_roll)
                pitch_diff = abs(pitch - desired_pitch)
                yaw_diff = abs(yaw - desired_yaw)
                #break and move to the next point if the error is within certain limit
                if(dist<0.5 and roll_diff < 0.1 and pitch_diff < 0.1 and yaw_diff < 0.1):
                    print("going to next")
                    break

            #finally save the data the path drone travelled in the csv file for plotting
            if(i==len(self.setpoints)):
                with open('data.csv',mode='w',newline='') as file:
                    writer=csv.writer(file)
                    writer.writerow(['x','y','z','time'])
                    for res in self.result:
                        writer.writerow([res[0],res[1],res[2],res[3]])
            i+=1



"""
main function

"""
if __name__ == '__main__':
    app = QApplication(sys.argv)
    drone_control = DroneControl()

    # Set window properties to fit the whole screen
    desktop = app.desktop()
    screen_rect = desktop.screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()
    drone_control.resize(width, height)

    # Center the window on the screen
    window_rect = drone_control.frameGeometry()
    window_rect.moveCenter(screen_rect.center())
    drone_control.move(window_rect.topLeft())
    #show ui
    drone_control.show()
    sys.exit(app.exec_())
