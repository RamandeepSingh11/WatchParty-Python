# [WatchParty-Python]
#### A python app to stream video files and chat with your friends in real time.

## Installing
```bash
pip3 install -r requirements.txt
```

## Configuring app
Before running the app you have to create a [ngrok](https://dashboard.ngrok.com/login) account. And download the ngrok [executable](https://ngrok.com/download) for your system. 

After doing the steps above add your ngrok authtoken in [Line 2](https://github.com/GamesBond008/WatchParty-Python/blob/master/config.json#L2) of config.json and ngrok executable path to the [Line 3](https://github.com/GamesBond008/WatchParty-Python/blob/master/config.json#L3) of config.json.

## Using the app

To run the app run the main.py file and click on either "Host a video" to stream a local file to people or "Connect to Host" to connect to the host.

### Selecting Host a Video
After Selecting Host a Video you should be able to pick up a video file afterwards the application will give you a prompt to copy a string which you should share to people to you want to stream.

### Selecting Connect to Host
After Selecting Connect to Host a prompt should come up which will ask for a string. You have to put the string that is shared by your friend in that prompt.

### Example Result
<img src="https://github.com/GamesBond008/WatchParty-Python/blob/master/Example/Sample.gif">
