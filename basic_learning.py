import pygame
import math
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)  # White
ROD_LENGTH = 200
ROD_WIDTH = 10
ROD_COLOR = (0, 0, 0)  # Black

# Box properties
BOX_WIDTH = 100
BOX_HEIGHT = 20
BOX_COLOR = (255, 0, 0)  # Red

# Wheel properties
WHEEL_RADIUS = 15
WHEEL_COLOR = (0, 0, 255)  # Blue

# Green ground properties
GROUND_HEIGHT = 20
GROUND_COLOR = (0, 255, 0)  # Green

# Physical constants
GRAVITY = 9.81  # Acceleration due to gravity (m/s^2)
ROD_MASS = 1.0  # Mass of the rod (kg)
ROD_MOMENT_OF_INERTIA = (1 / 3) * ROD_MASS * ROD_LENGTH ** 2  # Moment of inertia for a thin rod
VELOCITY_CHANGE = 1  # Adjust this to control the velocity change when the user presses left or right
# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rod Balance Simulation")

# Create an array to store lines and circles
objects = []

# Initialize artificial x-axis and x-axis range
x_axis = 0  # Start from 0
x_axis_min = 0  # Minimum x-axis value
x_axis_max = SCREEN_WIDTH  # Maximum x-axis value

# Initialize previous x-axis range
prev_x_axis_min = x_axis_min
prev_x_axis_max = x_axis_max

# Initialize rod angle
rod_angle = math.pi / 4  # Initial angle of the rod (45 degrees)

# Initialize angular velocity
angular_velocity = 0.0  # Initial angular velocity


reward_score = 0  # Initial reward score
old_reward_score = 0  # Initial old reward score
state = "right"
old_state = "stay"

# Function to calculate the reward based on the rod's angle
def calculate_reward(angle):
    # return 1 - abs(angle) / (math.pi / 2)  # Reward is 1 when the rod is vertical and 0 when the rod is horizontal
    global old_reward_score, reward_score
    old_reward_score = reward_score
    reward_score = 1 - abs(angle) / (math.pi / 2)  # Reward is 1 when the rod is vertical and 0 when the rod is horizontal

# Function to add a random object
def add_random_object(add="left"):
    obj_type = random.choice(["line", "circle"])
    if add == "left":
        obj_x = random.randint(int(x_axis_min) - SCREEN_WIDTH, int(x_axis_min))  # Ensure objects start within the current x-axis range
    elif add == "right":
        obj_x = random.randint(int(x_axis_max), int(x_axis_max) + SCREEN_WIDTH)  # Ensure objects start within the current x-axis range
    obj_y = random.randint(0, SCREEN_HEIGHT)
    if obj_type == "line":
        obj_length = random.randint(50, 200)
        line_color = (0, 0, 0)  # Black
        objects.append((obj_x, obj_y, obj_length, "line", line_color))
    else:
        obj_radius = random.randint(10, 30)
        circle_color = (255, 0, 255)  # Magenta
        objects.append((obj_x, obj_y, obj_radius, "circle", circle_color))

# Function to add random lines and circles
def add_random_objects():
    for _ in range(10):
        obj_type = random.choice(["line", "circle"])
        obj_x = random.randint(int(x_axis_min), int(x_axis_max))  # Ensure objects start within the current x-axis range
        obj_y = random.randint(0, SCREEN_HEIGHT)
        if obj_type == "line":
            obj_length = random.randint(50, 200)
            line_color = (0, 0, 0)  # Black
            objects.append((obj_x, obj_y, obj_length, "line", line_color))
        else:
            obj_radius = random.randint(10, 30)
            circle_color = (255, 0, 255)  # Magenta
            objects.append((obj_x, obj_y, obj_radius, "circle", circle_color))

# Add random objects at the start
add_random_objects()

# Q-Learning state initialization
def initialize_environment():
    # Return the current state based on the rod's angle and angular velocity
    return (rod_angle, angular_velocity)

# Q-Learning action selection
def select_best_action():
    # Calculate reward
    calculate_reward(rod_angle)

    global reward_score, old_reward_score, state, old_state,VELOCITY_CHANGE, angular_velocity
    VELOCITY_CHANGE = 1 - reward_score  # Adjust this to control the velocity change when the user presses left or right
    # only write per 20 frames to reduce the number of actions

    #print("Reward score:", reward_score)

    if reward_score == 0:
        # check if current movement is right or left from the velocity
        if angular_velocity < 0:
            old_state = state
            state = "right"
            return state
        elif angular_velocity > 0:
            old_state = state
            state = "left"
            return state
        else:
            old_state = state
            state = random.choice(["left", "right"])
            return state

   # Check the angular velocity and angle to determine the best action
    if angular_velocity > 0: # this means the rod is moving to the right
        if reward_score >= 0.99:
            old_state = state
            state = "stay"
            VELOCITY_CHANGE = 0.01
            return state
        # else if reward score is below 0.9 and angular velocity is above 0.1 then reverse the direction
        elif reward_score < 0.99 and angular_velocity > 1:
            old_state = state
            state = "left"
            return state


        # check if reward score is increasing or decreasing
        if reward_score > old_reward_score:
            old_state = state
            state = "right"
            return state
        else:
            old_state = state
            state = "left"
            return state
    elif angular_velocity < 0: # this means the box is moving to the left
        if reward_score >= 0.99:
            old_state = state
            state = "stay"
            VELOCITY_CHANGE = 0.01
            return state
        # else if reward score is below 0.9 and angular velocity is above 0.1 then reverse the direction
        elif reward_score < 0.99 and angular_velocity < -1:
            old_state = state
            state = "right"
            return state


        # check if reward score is increasing or decreasing
        if reward_score > old_reward_score:
            old_state = state
            state = "left"
            return state
        else:
            old_state = state
            state = "right"
            return state
    
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    # Draw the green ground
    pygame.draw.rect(screen, GROUND_COLOR, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

    # Draw lines and circles based on the artificial x-axis
    for obj in objects:
        obj_x, obj_y, obj_size, obj_type, obj_color = obj[0], obj[1], obj[2], obj[3], obj[4]
        obj_x -= x_axis  # Adjust x position based on artificial x-axis
        if 0 <= obj_x <= SCREEN_WIDTH:
            if obj_type == "line":
                pygame.draw.line(screen, obj_color, (obj_x, obj_y), (obj_x, obj_y - obj_size), ROD_WIDTH)
            elif obj_type == "circle":
                pygame.draw.circle(screen, obj_color, (obj_x, obj_y), obj_size)

    # Draw the rod
    rod_bottom_x = SCREEN_WIDTH // 2
    rod_bottom_y = SCREEN_HEIGHT - GROUND_HEIGHT - BOX_HEIGHT  # Bottom of the rod is aligned with the top of the box

    # Calculate the rod's position based on the current angle
    rod_top_x = rod_bottom_x - (ROD_LENGTH * math.sin(rod_angle))
    rod_top_y = rod_bottom_y - (ROD_LENGTH * math.cos(rod_angle))

    pygame.draw.line(screen, ROD_COLOR, (rod_bottom_x, rod_bottom_y), (rod_top_x, rod_top_y), ROD_WIDTH)

    # Draw the box
    box_left = rod_bottom_x - (BOX_WIDTH / 2)
    box_top = rod_bottom_y
    pygame.draw.rect(screen, BOX_COLOR, (box_left, box_top, BOX_WIDTH, BOX_HEIGHT))

    # Draw the wheels
    wheel1_x = box_left
    wheel2_x = box_left + BOX_WIDTH
    wheel_y = box_top + BOX_HEIGHT
    pygame.draw.circle(screen, WHEEL_COLOR, (int(wheel1_x), int(wheel_y)), WHEEL_RADIUS)
    pygame.draw.circle(screen, WHEEL_COLOR, (int(wheel2_x), int(wheel_y)), WHEEL_RADIUS)

    # Apply gravitational torque to the rod
    torque_due_to_gravity = -ROD_MASS * GRAVITY * (ROD_LENGTH / 2) * math.sin(rod_angle)
    angular_acceleration = torque_due_to_gravity / ROD_MOMENT_OF_INERTIA

    # Update angular velocity and angle
    angular_velocity += angular_acceleration * 0.02  # Fixed time step
    rod_angle += angular_velocity * 0.02  # Fixed time step

    # Ensure the rod angle stays within reasonable limits (-90 to 90 degrees)
    rod_angle = max(-math.pi / 2, min(math.pi / 2, rod_angle))

    # Apply control input (rotate left or right) 

    #draw a white background to the top left corner and the right top corner
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, 200, 60))
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - 200, 0, SCREEN_WIDTH, 60))

    # add 2 label to the top left corner green one is computer action and blue one is user action with a white background
    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("Computer Action ", True, (0, 0, 255))
    textRect = text.get_rect()
    textRect.center = (100, 20)
    screen.blit(text, textRect)

    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("User Action ", True, (0, 188, 0))
    textRect = text.get_rect()
    textRect.center = (100, 40)
    screen.blit(text, textRect)




    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        print("User Action: left")
        # draw left arrow at the left side of the screen at 200 pixel above the ground with a (0,188, 0) color 100 pixel right from the left side of the screen
        pygame.draw.polygon(screen, (0, 188, 0), ((100, SCREEN_HEIGHT - GROUND_HEIGHT - 200), (100, SCREEN_HEIGHT - GROUND_HEIGHT - 100), (0, SCREEN_HEIGHT - GROUND_HEIGHT - 150)))
        # add a label 10 pixel above the arrow with a white background and black color that says user action
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render("User Action ", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (100, SCREEN_HEIGHT - GROUND_HEIGHT - 210)
        screen.blit(text, textRect)

        angular_velocity -=  0.1
    elif keys[pygame.K_RIGHT]:
        print("User Action: right")
        # draw right arrow at the left side of the screen at 200 pixel above the ground with a (0,188, 0) color 100 pixel left from the right side of the screen
        pygame.draw.polygon(screen, (0, 188, 0), ((SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 200), (SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 150)))
        # add a label 10 pixel above the arrow with a white background and black color that says user action
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render("User Action ", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 210)
        screen.blit(text, textRect)

        angular_velocity += 0.1
    else:
        action = select_best_action()
        # draw dice and print if it is 2
        if random.randint(1, 3) == 2:    
            print("Computer Action:", action)
        if action == "left":
            # draw left arrow at the left side of the screen at 200 pixel above the ground with a (0,0, 255) color 100 pixel right from the left side of the screen
            pygame.draw.polygon(screen, (0, 0, 255), ((100, SCREEN_HEIGHT - GROUND_HEIGHT - 200), (100, SCREEN_HEIGHT - GROUND_HEIGHT - 100), (0, SCREEN_HEIGHT - GROUND_HEIGHT - 150)))
            # add a label 10 pixel above the arrow with a white background and black color that says computer action
            font = pygame.font.Font('freesansbold.ttf', 16)
            text = font.render("Computer Action ", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (100, SCREEN_HEIGHT - GROUND_HEIGHT - 210)
            screen.blit(text, textRect)

            angular_velocity -= VELOCITY_CHANGE
        elif action == "right":
            # draw right arrow at the left side of the screen at 200 pixel above the ground with a (0,0, 255) color 100 pixel left from the right side of the screen
            pygame.draw.polygon(screen, (0, 0, 255), ((SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 200), (SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT - 150)))

            # add a label 10 pixel above the arrow with a white background and black color that says computer action
            font = pygame.font.Font('freesansbold.ttf', 16)
            text = font.render("Computer Action ", True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT - GROUND_HEIGHT - 210)
            screen.blit(text, textRect)

            angular_velocity += VELOCITY_CHANGE

    # calculate the current speed as km/h
    speed = abs(angular_velocity * ROD_LENGTH / 2 * 3.6)
    # draw the speed on the right top corner
    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("Speed: " + str(round(speed / 1000, 2) ) + " km/h", True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (SCREEN_WIDTH - 100, 20)
    screen.blit(text, textRect)
    
    # calculate the current reward score
    calculate_reward(rod_angle)
    # draw the reward score on the right top corner
    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("Reward: " + str(round(reward_score, 2)), True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (SCREEN_WIDTH - 100, 40)
    screen.blit(text, textRect)




    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.delay(int(0.02 * 1000))  # Delay to achieve the desired time step

    # Update the artificial x-axis based on angular velocity
    x_axis += angular_velocity * 0.02 * 100  # Multiply by 100 to make the movement more visible

    # Update x-axis range based on changes in x_axis
    if x_axis < x_axis_min - 10:
        add_random_object("left")
        x_axis_min = x_axis
    elif x_axis > x_axis_max + 10:
        add_random_object("right")
        x_axis_max = x_axis


# Quit Pygame
pygame.quit()
