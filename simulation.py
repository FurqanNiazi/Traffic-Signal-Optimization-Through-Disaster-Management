import random
import time
import json
import threading
import pygame
import sys
import re
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="Please place your model key here")

# Initialize the Gemini client
model = genai.GenerativeModel('models/gemini-2.0-flash-exp')

# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultYellow = 2

signals = []
noOfSignals = 4
currentGreen = 0   
nextGreen = (currentGreen+1)%noOfSignals    
currentYellow = 0    

speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5, 'ambulance':3.0, 'fire_truck':2.8}

x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike', 4:'ambulance', 5:'fire_truck'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]

stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

stoppingGap = 15 
movingGap = 15   

pygame.init()
simulation = pygame.sprite.Group()

# Disaster variables
disaster_active = False
disaster_type = None  # 'flood' or 'earthquake'
affected_roads = []   # List of roads affected by the disaster

class TrafficSignal:
    def __init__(self, yellow, green):
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, is_emergency=False):
        pygame.sprite.Sprite.__init__(self)
        self.done = False
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.wait_time = 0
        self.is_emergency = is_emergency
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):    # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap         # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]
            
        # Set new starting and stopping coordinate
        if(direction=='right'):
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if(self.direction=='down'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
            if((self.y+self.image.get_rect().height<=self.stop or self.crossed == 1 or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                self.y += self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
            if((self.y>=self.stop or self.crossed == 1 or (currentGreen==3 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                self.y -= self.speed
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
            if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                self.x -= self.speed   
        elif(self.direction=='right'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):   # if the image has crossed stop line now
                self.crossed = 1
            if((self.x+self.image.get_rect().width<=self.stop or self.crossed == 1 or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                self.x += self.speed  # move the vehicle
        
        # Remove the vehicle if it has crossed the boundary
        if (self.x > 790 and self.y < 430) or (self.x < 595 and self.y > 430) or (self.y > 530 and self.x > 687) or (self.y < 340 and self.x < 687):
            if self.done == False:
                self.remove_from_lane()
            self.done = True
        

    def remove_from_lane(self):
        if self in vehicles[self.direction][self.lane]:
            vehicles[self.direction]['crossed'] += 1

# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()

def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green>0):   # while the timer of current green signal is not zero
        updateValues()
        time.sleep(1)
    currentYellow = 1   # set yellow signal on
    
    # reset stop coordinates of lanes and vehicles 
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow>0):  # while the timer of current yellow signal is not zero
        updateValues()
        time.sleep(1)
    time.sleep(1)
    currentYellow = 0   # set yellow signal off

    currentGreen = nextGreen
    repeat()  

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1

# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,5)  # Now includes emergency vehicles
        lane_number = random.randint(1,2)
        temp = random.randint(0,99)
        direction_number = 0
        dist = [25,50,75,100]
        
        if(temp<dist[0]):
            direction_number = 0
        
        elif(temp<dist[1]):
            direction_number = 1
        
        elif(temp<dist[2]):
            direction_number = 2
        
        elif(temp<dist[3]):
            direction_number = 3
        
        is_emergency = (vehicle_type == 4 or vehicle_type == 5)  # Ambulance or fire truck
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], is_emergency)
        
        time.sleep(1)
        
def get_traffic_state():
    state = {
        "currentGreen": currentGreen,
        "vehicles": {},
        "wait_times": {},
        "flow_rates": {},
        "emergency_vehicles": {}
    }
    for direction in directionNumbers.values():
        state["vehicles"][direction] = sum(len(vehicles[direction][lane]) for lane in [0, 1, 2]) - vehicles[direction]['crossed']
        state["wait_times"][direction] = sum(vehicle.wait_time for lane in vehicles[direction].values() if isinstance(lane, list) for vehicle in lane)
        state["flow_rates"][direction] = vehicles[direction]['crossed']
        state["emergency_vehicles"][direction] = sum(1 for lane in vehicles[direction].values() if isinstance(lane, list) for vehicle in lane if vehicle.is_emergency)
    return state

def get_decision_from_ai():
    global currentGreen, currentYellow, nextGreen

    while True:
        if signals[currentGreen].green == 0:
            state = get_traffic_state()

            # Ensure AI returns JSON
            prompt = f"""
### Traffic Signal Decision System ###

#### **Current Traffic State**
- **Current Green Light:** Road {state['currentGreen']}

#### **Vehicle Data:**
- **Total Vehicles on Each Road:**  
{json.dumps(state['vehicles'], indent=2)}

- **Total Wait Times (Seconds) on Each Road:**  
{json.dumps(state['wait_times'], indent=2)}

- **Emergency Vehicles on Each Road:**  
{json.dumps(state['emergency_vehicles'], indent=2)}

---

### **Decision Criteria**
1. **The road with the highest number of emergency vehicles must be prioritized first.**  
2. If multiple roads have the same highest number of emergency vehicles, select the one with the highest total vehicle count.  
3. If all roads have similar emergency and total vehicle counts, select the road with the longest wait time.  
4. The green light duration should be assigned based on the number of emergency vehicles and total traffic load.  
   - **More emergency vehicles → Longer duration**  
   - **Higher vehicle count → Medium duration**  
   - **Low vehicle count but long wait time → Short duration**  

---

### **Output Format**  
The response **must** be in **valid JSON format only** without explanations:  

```json
{{
    "nextGreen": <int>,  
    "defaultGreen": <int>
}}
"""
            #print(prompt)

            try:
                # Getting AI response
                analysis_results = model.generate_content(prompt)
                decision_text = analysis_results.candidates[0].content.parts[0].text.strip()

                print("Raw AI Response:", decision_text)

                # Remove markdown-style triple backticks if they exist
                match = re.search(r"```json\s*({.*})\s*```", decision_text, re.DOTALL)
                if match:
                    decision_text = match.group(1)  # Extract only the JSON part

                # Validate JSON format
                try:
                    decision = json.loads(decision_text)

                    if isinstance(decision, dict) and "nextGreen" in decision and "defaultGreen" in decision:
                        nextGreen = int(decision["nextGreen"])
                        if nextGreen < 0 or nextGreen >= noOfSignals:
                            raise ValueError("Invalid nextGreen value")
                        defaultGreen[nextGreen] = int(decision["defaultGreen"])

                        # Dynamic green time adjustment
                        gTime = defaultGreen[nextGreen]

                        # Adjust timing based on real traffic load
                        vehicle_count = state['vehicles'].get(nextGreen, 0)
                        if vehicle_count > 50:
                            gTime += 5
                        elif vehicle_count > 30:
                            gTime += 3
                        elif vehicle_count < 10:
                            gTime = max(2, gTime - 2)  # Ensure minimum time

                        print(f"Green: {nextGreen}, Time: {gTime}")

                        # Set traffic light durations
                        signals[nextGreen].green = gTime
                        signals[nextGreen].yellow = defaultYellow
                    else:
                        print("Invalid AI response format. Falling back to round-robin.")

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"AI response is not valid JSON or contains invalid data: {e}. Falling back to round-robin.")

            except Exception as e:
                print(f"Error in AI decision making: {e}")

        time.sleep(1)



class Main:
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()
    
    thread3 = threading.Thread(name="get_decision_from_ai", target=get_decision_from_ai, args=())
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background,(0,0))   # display background in simulation
        for i in range(0,noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if(i==currentGreen):
                if(currentYellow==1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["","","",""]

        # display signal timer
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i])

        # display the vehicles
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()
        
Main()
