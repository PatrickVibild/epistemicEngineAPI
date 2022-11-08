Epistemic Logic Engine
================================================================
Epistemic Logic Engine, developed to pass Sally Annie test.

##Installation
```
pip install -r requirements.txt
```

## Start

```
python main.py
```

## Interface

#### Reset Engine
```
curl --location --request PUT 'http://127.0.0.1:5500/reset'
```
#### Add vision between agents
Annie sees Sally and Sally sees Annie.

```
curl --location --request POST 'http://127.0.0.1:5500/sees' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sees":
    [
        ["Annie","Sally"],
        ["Sally", "Annie"]
    ]
}'
```
#### Remove vision between agents
Annie dont see Sally anymore.
```
curl --location --request DELETE 'http://127.0.0.1:5500/sees' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sees":
    [
        ["annie","sally"]
    ]
}'
```
#### Get Visions
```
curl --location --request GET 'http://127.0.0.1:5500/sees'
```
#### Add event
Annie removes cube from box1 and add cube to box3
```
curl --location --request POST 'http://127.0.0.1:5500/event' \
--header 'Content-Type: application/json' \
--data-raw '{
    "agent": "Annie",
    "event": "~In(cube,box1) AND In(cube,box3)"
}'
```
In this case, all agents that sees Annie will also have broadcasted a new state.