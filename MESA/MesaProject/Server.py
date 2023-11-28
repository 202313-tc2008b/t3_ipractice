import mesa

from agents import *
from model import StreetView


def street_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Road:
        portrayal["Color"] = ["#bec5cf", "#bec5cf", "#bec5cf"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if type(agent) is Buildings:
        portrayal["Color"] = ["#0390fc", "#0390fc", "#0390fc"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if type(agent) is ParkingSpots:
        portrayal["Color"] = ["#fcf803", "#fcf803", "#fcf803"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["text"] = agent.number
        portrayal["text_color"] = "black"

    if type(agent) is RoundAbout:
        portrayal["Color"] = ["#5e2a03", "#5e2a03", "#5e2a03"]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    if type(agent) is Stoplight:
        portrayal["Color"] = agent.color
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1


    if type(agent) is Car:
        portrayal["Color"] = ["#000", "#000", "#000"]
        portrayal["Shape"] = "arrowHead"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["scale"] = 1
        portrayal["heading_x"] = agent.current_direction[0]
        portrayal["heading_y"] = agent.current_direction[1]
        portrayal["text"] = agent.goal_spot
        portrayal["text_color"] = "white"

    return portrayal


canvas_element = mesa.visualization.CanvasGrid(street_portrayal, 24, 24, 576, 576)


model_params = {
    # The following line is an example to showcase StaticText.
    "title": mesa.visualization.StaticText("- Parameters -"),
    "buildings": mesa.visualization.StaticText("Buildings (Blue)"),
    "parkingSpots": mesa.visualization.StaticText("Parking Spots (Yellow)"),
    
}

server = mesa.visualization.ModularServer(
    StreetView, [canvas_element], "Street Mesa Simulation", model_params
)
server.port = 8521