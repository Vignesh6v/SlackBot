import os
import time
import re
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"


# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
area = []

class AreaFinder(object):
    """docstring for AreaFinder."""
    def __init__(self):
        self.area = []
        self.flag = False
        self.sides = 1
        self.pattern = re.compile('\d+(\.\d+)?')
        self.HELLO_COMMAND = "hello"
        self.TRIANGLE_COMMAND = "triangle"
        self.STOP_COMMAND = "stop"

    def calculate_area(self):
        l1,l2,l3 = self.area[0],self.area[1],self.area[2],
        if (l1>l2+l3) or (l2>l1+l3) or (l3>l1+l2):
            return -1
        else:
            s = (l1+l2+l3) / 2
            a = (s*(s-l1)*(s-l2)*(s-l3)) ** 0.5
            return a

    def getsides(self):
        if self.sides == 1:
            response = "What is length of the first edge ?"
        elif self.sides == 2:
            response = "What is length of the second edge ?"
        elif self.sides == 3:
            response = "What is length of the third edge ?"
        else:
            ans = self.calculate_area()
            if ans != -1:
                response = "Area of the triangle {}".format(ans)
            else:
                response = "Edges are not valid for a triangle "
            self.sides = 1
            self.flag = False
            self.area = []
        return response




def handle_command(command, channel, aObj):
    command = command.lower()
    response = "Not sure what you mean."
    print command

    if command == aObj.STOP_COMMAND:
        response = "Bye"
        aObj.sides = 1
        aObj.flag = False
        aObj.area = []
    elif command ==  aObj.HELLO_COMMAND and not aObj.flag:
        response = "Hello....!!!"
    elif command == aObj.TRIANGLE_COMMAND and not aObj.flag:
        aObj.flag = True
        response = aObj.getsides()
    else:
        if aObj.flag:
            if aObj.pattern.match(command):
                aObj.sides+=1
                aObj.area.append(float(command))
                response = aObj.getsides()
            else:
                response = "Enter a valid number"

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        aObj = AreaFinder()
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,aObj)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
