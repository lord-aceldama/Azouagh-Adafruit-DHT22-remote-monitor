import time
from datetime import datetime as DateTime
from typing import Optional, List, Dict

from telegram import Message
from telegram.ext import Updater, MessageHandler, Filters


#----------------------------------------------------------------------------------------------------------------------
# Alarm
THRESHOLD_TEMP = [15.0, 25.0, "Temperature", "°C"]
THRESHOLD_RH   = [0.0, 100.0, "Humidity", "%RH"]


# Telegram
TELEGRAM_BOT_API_KEY = 'YOUR API KEY HERE'


# Sensor
try:
    import Adafruit_DHT
except ImportError:
    print("WARN> using dummy driver. If you want to use an actual Adafruit DHT device, please install the pip.")
    import ada_dht as Adafruit_DHT
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4


#----------------------------------------------------------------------------------------------------------------------
# Globals
LOW, NORMAL, HIGH = (-1, 0, 1)
message_queue = []
recipients: Dict[str, Message] = {}


#----------------------------------------------------------------------------------------------------------------------
def send_message(text, message: Optional[Message] = None):
    """ Sends a message and keeps track of all recipients.

    :param text: The text to send (or add to the queue).
    :param message: The message object to reply to.
    :return:
    """
    global recipients

    # Register a user if one hasn't been set yet
    if (message is not None) and (type(message) is Message):
        recipients[message.from_user.username] = message

    # Send the message
    if len(recipients) == 0:
        # No recipients yet so add it to the queue
        message_queue.append([DateTime.now(), text])
    else:
        # Send it
        for sender in recipients:
            recipients[sender].reply_text(text)
            if len(message_queue) > 0:
                # Send any messages that weren't seen yet
                recipients[sender].reply_text("There were also some unread messages while you were away.")
                while len(message_queue) > 0:
                    popped = message_queue.pop()
                    recipients[sender].reply_text(f"{popped[0]:%Y/%m/%d %H%M%S}\n\n{popped[1]}")


def command_handler(update, context):
    """ Handles user commands. """
    global recipients

    clean_text: str = update.message.text.strip().lower()
    if clean_text in ["/start", "hi", "hello", "howdy"]:
        # Greet the user
        send_message("Well, howdy partner!", update.message)
    elif clean_text in ['temp', 'rh', 'data']:
        # User requested details
        ada_rh, ada_temp = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if None in [ada_rh, ada_temp]:
            send_message("The sensor is currently down.", update.message)
        else:
            if clean_text == "temp":
                send_message(
                    f"The current {THRESHOLD_TEMP[2].lower()} is {ada_temp:.2f}{THRESHOLD_TEMP[3]}.",
                    update.message
                )
            if clean_text == "temp":
                send_message(
                    f"The current {THRESHOLD_RH[2].lower()} is {ada_rh:.2f}{THRESHOLD_RH[3]}.",
                    update.message
                )
            else:
                send_message(
                    f"The current sensor reading is {ada_temp:.2f}{THRESHOLD_TEMP[3]} at " +
                    f"{ada_rh:.2f}{THRESHOLD_RH[3]}.",
                    update.message
                )
    elif clean_text in ["forget", "shut up", "quiet", "mute"]:
        # Mute the bot for current user
        send_message(f"You'll no longer receive updates. Just message me if you want them again.", update.message)
        recipients.pop(update.message.from_user.username)
    elif clean_text == "ping":
        # Request pong
        send_message(f"pong", update.message)
    elif clean_text in ["list", "users", "recipients"]:
        user_list = recipients.keys()
        send_message(f"There are {len(user_list)} receiving updates: {', '.join(user_list)}", update.message)
    else:
        send_message(f"I don't know what '{clean_text}' means.", update.message)


#----------------------------------------------------------------------------------------------------------------------
def monitor_threshold(bound: List, value: float, current_status: int) -> int:
    """ Notifies the user if a reading changed between LOW, NORMAL or HIGH.

    :param bound: Either THRESHOLD_RH or THRESHOLD_TEMP.
    :param value: The current value for the sensor reading.
    :param current_status: The current status. (ie. LOW, NORMAL or HIGH)
    :return: The new status.
    """
    result = NORMAL
    if (current_status != NORMAL) and (bound[0] <= value <= bound[1]):
        send_message(f"{bound[2]} has re-entered normal range. It's currently {value}{bound[3]}")
    elif bound[0] > value:
        # Value too low
        result = LOW
        if current_status != LOW:
            # Status changed
            send_message(
                f"{bound[2]} too low! Current value is {value:.2f}{bound[3]} (threshold: {bound[0]:.2f}{bound[3]})"
            )
    elif value > bound[1]:
        # Temp too high
        result = HIGH
        if current_status != HIGH:
            # Status changed
            send_message(
                f"{bound[2]} too high! Current value is {value:.2f}{bound[3]} (threshold: {bound[1]:.2f}{bound[3]})"
            )
    else:
        pass  # We should never end up here

    return result


def monitor_sensor(old_status: bool, new_status: bool) -> bool:
    """ Notifies the user if the sensor status changed from off-to-online or vise versa.

    :param old_status: The current status of the sensor.
    :param new_status: The new status of the sensor.
    :return: The new status of the sensor.
    """
    if old_status != new_status:
        if new_status:
            send_message(f"Sensor has gone back online.")
        else:
            send_message(f"Sensor has gone offline.")

    return new_status


#----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main
    """
    # Init bot
    updater = Updater(TELEGRAM_BOT_API_KEY, use_context=True)

    # Add handler(s)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, command_handler))

    # Start bot
    updater.start_polling()
    try:
        # Monitor temp
        status_temp = 0
        status_rh = 0
        sensor_online = True
        while True:
            # Poll the sensor
            ada_rh, ada_temp = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

            # Check the data
            sensor_online = monitor_sensor(sensor_online, None not in [ada_rh, ada_temp])
            if sensor_online:
                status_temp = monitor_threshold(THRESHOLD_TEMP, ada_temp, status_temp)
                status_rh = monitor_threshold(THRESHOLD_RH, ada_rh, status_rh)

            time.sleep(5)

    except KeyboardInterrupt:
        print("User quit with keyboard interrupt.")

    updater.stop()


#----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
