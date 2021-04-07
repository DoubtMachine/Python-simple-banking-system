# Write your code here
import random
import sqlite3

conn = sqlite3.connect('card.s3db', timeout=10)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS card')
conn.commit()
cur.execute(
    'CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()


def menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    answer = int(input())
    if answer == 1:
        new_card()
    if answer == 2:
        login()
    if answer == 0:
        print('Bye!')
        exit()


def findRoundNumber(order):
    s = order % 10
    return 0 if s == 0 else (10 - s)


def luhn(new_number, is_first_time=True):
    steps = 0
    # print(new_number)
    checksum_list = []
    for digit in new_number:
        steps += 1
        # print(digit, steps)
        if steps % 2 != 0:
            new_digit = int(digit) * 2
            if new_digit > 9:
                new_digit -= 9
                checksum_list.append(new_digit)
            else:
                checksum_list.append(new_digit)
        else:
            checksum_list.append(int(digit))
    # print(sum(checksum_list))
    if is_first_time is False:
        last_item = checksum_list[-1]
        new_checksum_list = checksum_list[:]
        del new_checksum_list[-1]
        checksum = sum(new_checksum_list)
        if (checksum + last_item) % 10 != 0:
            print(checksum + last_item)
            if is_first_time:
                new_card(1)
            else:
                return False
        else:
            return True
    else:
        checksum = sum(checksum_list)
        # Below the last number of the credit card
        return new_number + str(findRoundNumber(checksum))
    # print(new_number)


def new_card(attempt=0):
    if attempt == 0:
        print("Your card has been created")
        print("Your card number:")
        attempt += 1
    if attempt != 0:
        new_number = "400000"
        new_number += str(random.randrange(100000000, 999999999))
        new_number = luhn(new_number)
        print(new_number)
        print("Your card PIN:")
        new_pin = random.randrange(1000, 9999)
        print(new_pin)

        conn.execute(f'INSERT INTO card (number, pin, balance) VALUES ({new_number}, {new_pin}, 0)')
        conn.commit()
        menu()


def login():
    card_no = input("Enter your card number:")
    entered_pin = int(input("Enter your PIN:"))
    cur.execute(f'SELECT number, pin FROM card WHERE number = {card_no} AND pin = {entered_pin}')
    conn.commit()
    result = cur.fetchall()
    print(result)
    if any(card_no in i for i in result):
        print("You have successfully logged in!")
        logged_in(card_no, entered_pin)
    else:
        print("Wrong card number or PIN!")
        menu()


def logged_in(num, pwd):
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    answer = int(input())
    cur.execute(f'SELECT balance FROM card WHERE number = {num} AND pin = {pwd}')
    conn.commit()
    bal = [int(record[0]) for record in cur.fetchall()]
    if answer == 1:
        print(f"Balance: {bal[0]}")
    if answer == 2:
        print("Enter income:")
        income = int(input())
        cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {num}")
        conn.commit()
        # cur.execute("SELECT * FROM card")
        # print(cur.fetchall())
        print("Income was added!")
        logged_in(num, pwd)
    if answer == 3:
        print("Transfer")
        print("Enter card number:")
        transfer = input()
        curser = conn.execute(f"""SELECT number FROM card WHERE number = {transfer}""")
        q = curser.fetchall()
        print(q)
        if luhn(transfer, False) is False:
            print("Probably you made a mistake in the card number. Please try again!")
            logged_in(num, pwd)
        if not any(transfer in i for i in q):
            print(q)
            # print(luhn(transfer, False))
            print("Such a card does not exist.")
            logged_in(num, pwd)
        if any(transfer in i for i in q):
            print("Enter how much money you want to transfer:")
            money = int(input())
            if money > bal[0]:
                print("Not enough money!")
                logged_in(num, pwd)
            elif transfer == num:
                print("You can't transfer money to the same account!")
                logged_in(num, pwd)
            else:
                cur.execute(f"UPDATE card SET balance = balance + {money} WHERE number = {transfer}")
                conn.commit()
                cur.execute(f"UPDATE card SET balance = balance - {money} WHERE number = {num}")
                conn.commit()
                print("Success!")
                menu()

    if answer == 4:
        cur.execute(f"DELETE FROM card WHERE number = {num} AND pin = {pwd}")
        conn.commit()
        print("The account has been closed!")
        menu()
    if answer == 5:
        print('You have successfully logged out!')
        menu()
    if answer == 0:
        print('Bye!')
        cur.close()
        conn.close()
        exit()


# Execute some sql query
# cur.execute('SOME SQL QUERY')
# After you do some changes save (commit) them
# conn.commit()

menu()
