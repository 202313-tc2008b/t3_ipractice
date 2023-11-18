# Integrative activity

## Engineering the Problem

### Team 3:

- Moisés Arturo Badillo Álvarez
- Jonathan Josué Fuentes Ramírez
- Alejandro Pozos Aguirre
- Andrew Steven Williams Ponce

## Problem

Having two systems (MA, CG) that operate remotely and communicate with web requests to present a coordinated solution.

Problems to solve with design, before implementation:

### Size of the environment (units, measures).
  
Since the size of the map is of 24x24 tiles, the size of the environment will be 24x24. 
Working with homogenous transformations it will be easier to take each tile as 10x10 units. Therefore, the map will measure:

- 240 homogenous units in x axis
- 240 homogenous units in z axis

### Replicating navigation

We then must ask ourselves: How to replicate the navigation space in both systems (MA, CG)?

We need to use MESA. MESA has support for models that work with grids. 

Each grid can be:

- A road
- A crossline (with a stoplight)
- A parking spot
- A building

The cars may change of lane, but shall not go in lanes that go in lanes of the opposite direction. 

The idea is that the Flask server with MESA can send JSON files to the Unity and viceversa. This way the game will know the state of the simulation in server and the server will know the state of the Unity simulation.

### How to coordinate the number of agents in both systems (MA, CG).

The MA system shall dictate the number of agents in the sim. The CG system will receive this information in form of a JSON message, along with other data.

- Establish the protocol to exchange JSON messages (POST, GET, messages).

The information will be transmitted through POST and GET HTML requests.

- POST: CG in Unity >> MA in Flask
- GET: CG in Unity << MA in Flask

- Establish the required JSON format to exchange messages.
  
```JSON```

```json
{
    {
    "cars": [ // Array of Car Agents
        {
            "car_id": 1, // ID of the car instance
            "pos": { // position in the grid
                "x": 10,
                "y": 20 // z in Unity
            },
            "status": true // stopped or driving
        },
        {
            "car_id": 2,
            "position": {
                "x": 15,
                "y": 25
            },
            "status": false
        }.
        ...
        // Add more cars as needed
    ],
    "stoplights": [ // Array of Stoplights
        {
            "stoplight_id": 101, // ID of the semaphore
            "light": "R" // Red (R), Yellow (Y), or Green (G)
        },
        {
            "stoplight_id": 102,
            "light": "G"
        },
        ...
        // Add more stoplights as needed
    ]
}

}
```

- How to optimize the frequency and size of JSON messages to share.

It is hard to decide on the frequency and size of JSON messages. 
On one hand, in a big scale simulation, many small JSON messages (i.e. one for each agent/instance) may be unoptimal. However, a big files that contains the informationn of all agents in JSON arrays might actually be the optimal solution for this case, since we shall not have that much agents. In a massive simulation, more complex networking engineering would be needed to create massive games like MMOs, but that is far from the scope of this project.

Ideally, it would look something like this:

- One JSON for All Cars and All Stoplights

With this system, the Server will only have to send one JSON in each step, and the Unity server will only export one state at a time.

### How to synchronize time in both systems.
  
Time works differently in both systems. Ideally, the MA system will go step by step. One step in the MA will correpond to a certain number of frames in CG. 

### Information absence

How to manage information abscence when agents positions cannot be shared in real-time? Ideally, both systems will have a certain amount of independence from each other.

However, this sets a real dilemma unto our shoulders. How can we know that the system is still on-line. For that, one may think that a session should be established, with advanced networking. We think this is out of scope for this project, given the few time we possess. 