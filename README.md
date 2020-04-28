# CS Build Week 1

For your first CS Build Week, you will be building an interactive ***Multi-User Dungeon (MUD)*** client and server in groups. To succeed with this project, you will be applying knowledge you've learned throughout the first part of CS to this project.

You should treat this like a real-world job assignment with your instructor as the client. Like in the real world, you may not be given all the information you need to complete the assignment up front. It is your responsibility to understand the requirements and ask questions if anything is unclear (UPER) before jumping into the code.

### What is a MUD?
>A MUD...is a multiplayer real-time virtual world, usually text-based. MUDs combine elements of role-playing games, hack and slash, player versus player, interactive fiction, and online chat. Players can read or view descriptions of rooms, objects, other players, non-player characters, and actions performed in the virtual world. Players typically interact with each other and the world by typing commands that resemble a natural language. - Wikipedia

With the adventure game built in previous weeks, you have already created an application containing some of these elements (rooms, descriptions, objects, players, etc.). In this project, we will be expanding these worlds to be more interactive, provide new actions for players, display world info on a professional client site, and run the world's server on a hosted site to allow multi-player functionality.

## Deliverables

Each team is responsible for building and deploying a functional MUD server, migrating a unique world onto that server, and creating a visualization and navigation client interface. We provide starter Flask code with much of the server functionality implemented.


### Server


#### 1. Learn Flask

In Sprint 1, you learned a new language (Python) and built an interactive world with it. During this project, you will be learning a new REST API framework (Flask) and building a more interesting world.


#### 2. Implement Login

You have been given code for Registration but will need to implement login and token authentication in Flask.

Token authentication should be identical to the Django version of the project. As in, registration and login should return 40-character authentication key which must be passed in the header of every subsequent authenticated API request.


#### 3. Implement Item classes

Similar to your Intro to Python adventure project, the Item base class should be able to be picked up and dropped, bought and sold. You are required to have at least 2 types of Item subclasses.

Suggestions for item subclasses:
  - Food
  - Clothing
  - Light Source
  - Weapon


#### 4. Implement Store

You must create a store where items can be bought and sold.


#### 5. Implement Pusher Websockets

Your server should create websocket connections with each client upon initialization and broadcast messages where appropriate.

This NOT a stretch goal and is required for MVP.


#### 6. Create an interesting world on the server

You will need to create more rooms and descriptions to build a unique, traversable world that your client apps can interact with via REST API calls.

Your world should contain a MINIMUM of 100 connected rooms.

You will also need to implement a GET `rooms` API endpoint for clients to fetch all rooms to display a map on the frontend.


#### 7. Deploy a Flask LambdaMUD server

Research and deploy your Flask server on Heroku.


### Client

#### 1. Deploy a LambdaMUD client that connects to the test server

While your backend developers are implementing your production server, you may test your endpoints on the test server hosted at `https://lambda-mud-test.herokuapp.com/`. You can use this to test your interface for account registration, login, movement and map display. (See sample API commands below.) Your app should store the user's auth token upon successful registration/authentication and use it to authenticate subsequent API requests.

#### 2. Connect your LambdaMUD client to the production server

Once your backend is up and running, you should be able to swap out the test host URL for your production URL and interact with your production server.

#### 3. Display a visual map of the world

Your backend should implement a `rooms` endpoint which will return data for every room in your world. Your job will be to build a map to display a map of those rooms, along with relevant information, like marking which room the player is currently in.

#### 4. Implement Store and Inventory functionality

Create an interface to pick up and drop items, and buy and sell them from a store.

#### 5. Implement client "hearing" (Brady walks in from the north) and chat using the Pusher websocket library.

This NOT a stretch goal and is required for MVP.



## API Requirements

These are implemented on the test server: `https://lambda-mud-test.herokuapp.com/`.

### Registration
* `curl -X POST -H "Content-Type: application/json" -d '{"username":"testuser", "password1":"testpassword", "password2":"testpassword"}' localhost:8000/api/registration/`
* Response:
  * `{"key":"6b7b9d0f33bd76e75b0a52433f268d3037e42e66"}`

### Login
* Request:
  * `curl -X POST -H "Content-Type: application/json" -d '{"username":"testuser", "password":"testpassword"}' localhost:8000/api/login/`
* Response:
  * `{"key":"6b7b9d0f33bd76e75b0a52433f268d3037e42e66"}`

### Initialize
* Request:  (Replace token string with logged in user's auth token)
  * `curl -X GET -H 'Authorization: Token 6b7b9d0f33bd76e75b0a52433f268d3037e42e66' localhost:8000/api/adv/init/`
* Response:
  * `{"uuid": "c3ee7f04-5137-427e-8591-7fcf0557dd7b", "name": "testuser", "title": "Outside Cave Entrance", "description": "North of you, the cave mount beckons", "players": []}`

### Move
* Request:  (Replace token string with logged in user's auth token)
  * `curl -X POST -H 'Authorization: Token 6b7b9d0f33bd76e75b0a52433f268d3037e42e66' -H "Content-Type: application/json" -d '{"direction":"n"}' localhost:8000/api/adv/move/`
* Response:
  * `{"name": "testuser", "title": "Foyer", "description": "Dim light filters in from the south. Dusty\npassages run north and east.", "players": [], "error_msg": ""}`
* Pusher broadcast (stretch):
  * Players in previous room receive a message: `<name> has walked north.`
  * Players in next room receive a message: `<name> has entered from the south.`

### Say
* Request:  (Replace token string with logged in user's auth token)
  * `curl -X POST -H 'Authorization: Token 6b7b9d0f33bd76e75b0a52433f268d3037e42e66' -H "Content-Type: application/json" -d '{"message":"Hello, world!"}' localhost:8000/api/adv/say/`
* Pusher broadcast:
  * Players in current room receive a message: `<name> says "Hello, world!"`

## Pusher

WebSocket is a computer communications protocol, providing full-duplex communication channels over a single TCP connection. You may use the Pusher service to handle the WebSocket connections as a stretch goal for your project. You can read more about them [here](https://pusher.com/websockets).

### Set up a Pusher account
* Sign up for a free account on pusher.com
* Create a new app
* Take note of your credentials
  * app_id, key, secret, cluster
* Look through the provided sample code and documentation


## FAQs and Troubleshooting

### 1. Can you show me an example of a map visualization?

Here's a sample project created by [a team in CSPT2](https://confident-wright-ca0176.netlify.com):

![Lambda MUD 1](img/pt2_lambdamud.png)

And here's [a FT team](https://lambdaschool.com/lab-demos/lambda-mud) that went above and beyond with their use of graphics:

![Lambda MUD 2](img/ex_lambdamud.png)

And here's an example on iOS:

![Lambda MUD Mobile](img/ios_lambdamud.jpg)

### 2. How do I build something like that?

Think about the algorithm to draw your map. It will probably be something like this:

```
def draw_map():
    # Get all rooms
    # For each room in rooms...
        # Draw the room
        # Draw each exit
```

What data do you need to implement this? A list of rooms, their exits, maybe their positions? The server should return all the information you need from the `rooms` endpoint. Note that backend developers may need to define some fields in the `Room` model that do not exist yet.

### 3. How do I "create an interesting world"?

I'll leave that to you to determine.


### 4. What is Pusher?

Pusher is a cross-platform websocket library. This will allow you to turn your app into a real MUD with live push notifications to your client. You can consider integration to be a stretch goal but it's worth the effort if you have the time: websockets are powerful!


### 5. What will the `rooms` API endpoint look like?

It's up to you what data the request will return but the API request should be something like this:

```
curl -X GET -H 'Authorization: Token cc504e88ef659843b858d61c101ca9d4f0edf979' http://lambda-mud-test.herokuapp.com/api/adv/rooms/
```

