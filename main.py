import sqlite3
import os
# java_path = "C:/Program Files/Java/jdk1.8.0_111/bin/java.exe"
# os.environ['JAVAHOME'] = java_path
import nltk
# nltk.internals.config_java('C:/Program Files/Java/jre1.8.0_271/bin/java.exe')
from experta import *
from nltk import StanfordNERTagger
from datetime import datetime

import bfare
import test
import discord
from discord.ext import commands
import queueBot

st = StanfordNERTagger(
    '/home/shinzie/PycharmProjects/RailBot/stanford-ner-2020-11-17/classifiers/english.muc.7class.distsim.crf.ser.gz',
    '/home/shinzie/PycharmProjects/RailBot/stanford-ner-2020-11-17/stanford-ner.jar',
    encoding='utf-8')
conn = sqlite3.connect('database.db')
c = conn.cursor()


class checkDetails(KnowledgeEngine):

    @Rule(Fact(outbound_date=L('empty')),
          Fact(from_outbound=MATCH.from_outbound))
    def ask_outbound_date(self, from_outbound):
        output_str = "What date do you want to travel from " + str(from_outbound) + "?"
        print("1")
        queueBot.outputq.put(output_str)

        while True:
            user_input = queueBot.inputq.get()
            date = test.contains_date(user_input)
            if date != 'empty':
                if not test.compare_to_now(False, date):
                    self.declare(Fact(outbound_date=date))
                    # sample_Journey.set_outbound_date(date) # for unit testing only
                    booking1.set_outbound_date(date)
                    break
                else:
                    print("2")
                    queueBot.outputq.put("Your outward journey is in the past. Please enter valid date.")
            else:
                print("3")
                queueBot.outputq.put("Sorry, I can't understand. Please use format DD/MM/YY.")

    # require outbound date (type datetime.date)
    @Rule(Fact(outbound_time=L('empty')),
          Fact(outbound_date=MATCH.outbound_date))
    def ask_outbound_time(self, outbound_date):
        # cast outbound_date to datetime.datetime obj
        # print(outbound_date)
        output_str = "What time do you want to travel on " + str(outbound_date) + "?"
        print("4")
        queueBot.outputq.put(output_str)

        while True:
            user_input = queueBot.inputq.get()
            time = test.contains_time(user_input)

            if time != 'empty':
                t = time.split(':')
                hour = int(t[0])
                minute = int(t[1])
                year = outbound_date.year
                month = outbound_date.month
                day = outbound_date.day
                date_time = datetime(year, month, day, hour, minute)
                if not test.compare_to_now(True, date_time):
                    self.declare(Fact(outbound_time=time))
                    # sample_Journey.set_outbound_time(time) # for unit testing only
                    booking1.set_outbound_time(time)
                    break
                else:
                    output_str = "Sorry the train at" +  time + "has departed."
                    print("5")
                    queueBot.outputq.put(output_str)
            else:
                print("6")
                queueBot.outputq.put("Sorry, I can't understand. Please use format (HH:MM).")

    @Rule(Fact(return_date=L('empty')),
          Fact(journey_type=L('return')),
          Fact(outbound_date=MATCH.outbound_date))
    def ask_return_date(self, outbound_date):
        print("7")
        queueBot.outputq.put("What date do you want to return?")

        while True:
            temp = queueBot.inputq.get()
            date = test.contains_date(temp)
            if date != 'empty':
                if test.compare_dates(False, outbound_date, date):
                    # sample_Journey.set_return_date(date) # for unit testing only
                    booking1.set_return_date(date)
                    self.declare(Fact(return_date=date))
                    break
                else:
                    print("8")
                    queueBot.outputq.put("Your return journey is earlier than your outward journey.")
            else:
                print("9")
                queueBot.outputq.put("Sorry, I can't understand. Please use format DD/MM/YY.")

    @Rule(Fact(journey_type=L('return')),
          Fact(return_time=L('empty')),
          Fact(return_date=MATCH.return_date),
          Fact(outbound_date=MATCH.outbound_date),
          Fact(outbound_time=MATCH.outbound_time))
    def ask_return_time(self, return_date, outbound_date, outbound_time):
        output_str = "What time do you want to return on " + str(return_date) + "?"
        print("10")
        queueBot.outputq.put(output_str)
        year = return_date.year
        month = return_date.month
        day = return_date.day

        while True:
            user_input = queueBot.inputq.get()
            inbound_time = test.contains_time(user_input)
            if inbound_time != 'empty':
                temp = inbound_time.split(':')
                hour = int(temp[0])
                minute = int(temp[1])

                y = outbound_date.year
                m = outbound_date.month
                d = outbound_date.day
                out_time = outbound_time.split(':')
                h = int(out_time[0])
                min = int(out_time[1])

                inbound_date_time = datetime(year, month, day, hour, minute)
                outbound_date_time = datetime(y, m, d, h, min)
                if test.compare_dates(True, outbound_date_time, inbound_date_time):
                    self.declare(Fact(return_time=inbound_time))
                    # sample_Journey.set_return_time(inbound_time) # for unit testing only
                    booking1.set_return_time(inbound_time)
                    break
                else:
                    output_str = "Sorry you can't travel on " + str(return_date) + \
                          " at "+ inbound_time + " if you are leaving at " + outbound_time
                    print("11")
                    queueBot.outputq.put(output_str)
            else:
                output_str = "Sorry I didn't catch that. Please enter the travel time on "+ str(return_date)+ "."
                print("12")
                queueBot.outputq.put(output_str)


if __name__ == '__main__':

    '''
    ======== Unit testing ========
    sample_test_ask_outbound_date() 
    sample_test_ask_outbound_time() 
    sample_test_ask_return_date() 
    sample_test_ask_return_time() 
    print(">> Integration test for Task 1... ")
    '''

    ''' ======== Main system here ======== '''

    reset = True
    print("13")
    queueBot.outputq.put(
        "Hello! I am a bot for train operating company. I can help you find the cheapest train ticket.")

    while reset:
        reset = False
        print("14")
        queueBot.outputq.put("Please type in your journey details..")

        # example = "I want to go from Norwich to London King's Cross on Feb 10th at 07:00 and return on Feb 13th. "
        booking1 = test.myBooking(queueBot.inputq.get())

        engine = checkDetails()
        engine.reset()  # Prepare the engine for the execution
        if booking1.get_outbound_date() == 'empty':
            engine.ask_outbound_date(booking1.get_outbound())
        if booking1.get_outbound_time() == 'empty':
            engine.ask_outbound_time(booking1.get_outbound_date())
        if booking1.get_journey_type() == 'return':
            if booking1.get_return_date() == 'empty':
                engine.ask_return_date(booking1.get_outbound_date())
            if booking1.get_return_time() == 'empty':
                engine.ask_return_time(booking1.get_return_date(), booking1.get_outbound_date(),
                                       booking1.get_outbound_time())
        ''' To ask for a return journey '''
        if booking1.get_journey_type() == 'single':
            print("15")
            queueBot.outputq.put("Do you need a return journey? Please reply 'yes' or 'no'.")
            respond = queueBot.inputq.get()
            if respond.lower() == "yes" or respond.lower() == "y":
                print("16")
                queueBot.outputq.put("Okay. Please enter a few more details.")
                booking1.set_journey_type('return')
                engine.reset()
                engine.ask_return_date(booking1.get_outbound_date())
                engine.ask_return_time(booking1.get_return_date(), booking1.get_outbound_date(),
                                       booking1.get_outbound_time())  # Run it!

        booking1.confirm_details()

        confirm = queueBot.inputq.get()
        if confirm.lower() == "yes" or confirm.lower() == "y":  # Correct details
            print("17")
            queueBot.outputq.put("Great! Let me find the cheapest ticket for you")
            find_ticket = bfare.trainFinder(booking1)
            response = find_ticket.makeQuery()
            if response == 'not found':
                print("18")
                queueBot.outputq.put("It seems that no tickets are available.")
            ''' 
            else: 
                print("Bot: Is there anything else I can do for you?")
                ========================================
                ========= Task 2 continue here =========
                ========================================
            '''
        elif confirm.lower() == "no" or confirm.lower() == "n":  # Incorrect details
            print("19")
            queueBot.outputq.put("Okay. Do you want to start over? (y/n)")
            query = queueBot.inputq.get()
            if query.lower() == "yes" or query.lower() == "y":
                reset = True

        print("20")
        queueBot.outputq.put("Do you want to book another ticket? (y/n)")
        another = queueBot.inputq.get()
        if another.lower() == "yes" or another.lower() == "y":  # Correct details
            reset = True
    print("21")
    queueBot.outputq.put("Thank you for using our service. Bye!")
