import random
import sqlite3
from typing import List


class Bank:

    def __init__(self):
        self.accounts_logged_in = {}

        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()

        #  Check, if DataBase doesn't exists, create it
        self.cur.execute(
            """SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';""".format(table_name='card'))
        if self.cur.fetchone() != ('card',):
            self.cur.execute("""
            CREATE TABLE card (
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                )
            """)
            self.conn.commit()

            self.cur.execute("""
                INSERT INTO card VALUES(
                    1,
                    'admin',
                    'admin_pass',
                    0
                )
            """)
            self.conn.commit()

    @staticmethod
    def last_luhn_digit(card_15: str) -> str:
        """
        Calculate the last digit of 16-digits card number, according to Luhn algorithm

        :param card_15: card number without the last digit
        :return: the last digit
        """
        card_list_str = list(card_15)
        card_list_int = [int(i) for i in card_list_str]

        for i in list(range(0, 15, 2)):
            card_list_int[i] *= 2
            if card_list_int[i] > 9:
                card_list_int[i] -= 9

        last_digit = sum(card_list_int) % 10
        if last_digit != 0:
            last_digit = 10 - last_digit
        last_digit_str = str(last_digit)

        return last_digit_str

    @staticmethod
    def luhn_pass(card_16: str) -> bool:
        """
        Check, if input card number pass Luhn algorithm or not
        :param card_16: card number
        :return: Boolean
        """
        last_luhn_digit = Bank.last_luhn_digit(card_16[:-1])
        return card_16[-1] == last_luhn_digit

    @staticmethod
    def card_construction() -> str:
        """
        Construct a card number for new user
        :return: card number
        """
        bik_str = "400000"
        card_id = random.randint(100000000, 999999999)
        card_id_str = str(card_id)
        card_15 = bik_str + card_id_str

        last_digit = Bank.last_luhn_digit(card_15)
        card_16 = card_15 + last_digit

        return card_16

    def number_in_base(self, card: str) -> bool:
        """
        Check, whether card number already exists in the DataBase
        :param card:
        :return: Boolean
        """
        self.cur.execute("""SELECT number FROM card""")
        numbers = self.cur.fetchall()
        return (card,) in numbers

    def last_id(self) -> str:
        """
        The last ID number of the customer
        :return:
        """
        self.cur.execute("""SELECT MAX(id) FROM card""")
        return self.cur.fetchone()[0]

    def create_account(self):
        """
        Creates account in DataBase
        :return: Log message
        """
        bank_id = self.last_id() + 1
        number = self.card_construction()
        while self.number_in_base(number):
            number = Bank.card_construction()
        pin = random.randint(1000, 9999)

        self.cur.execute("""
                         INSERT INTO card (id, number, pin)VALUES
                         ({bank_id}, {number}, {pin})
                         """.format(bank_id=bank_id,
                                    number=number,
                                    pin=pin))
        self.conn.commit()

        print("Your card has been created\n"
              "Your card number:\n"
              "{number}\n"
              "Your card PIN:\n"
              "{pin}\n".format(number=number, pin=pin))

    def login(self, card: str, pin: str):
        """
        Logins user to banking system
        :param card: card number
        :param pin: card pin
        :return: Log message
        """
        if self.number_in_base(card):
            self.cur.execute("""
                             SELECT pin 
                             FROM card 
                             WHERE number = {card}
                             """.format(card=card))
            pin_in_base = self.cur.fetchone()[0]

            if pin == pin_in_base:
                print('You have successfully logged in!\n')
                self.accounts_logged_in[card] = {}
                self.accounts_logged_in[card]['login'] = 1
            else:
                print("Wrong card number or PIN!\n")
        else:
            print("Wrong card number or PIN!\n")

    def get_balance(self, card: str) -> int:
        """
        Getting balance of chosen card
        :param card: card number
        :return: Balance
        """
        self.cur.execute("""
                         SELECT balance 
                         FROM card
                         WHERE number = {card}"""
                         .format(card=card))
        return self.cur.fetchone()[0]

    def balance_change(self, card: str, income: int, method: List[str] = ('plus', 'minus')):
        """
        Changes balance of chosen card. Add or subtract
        :param card: card number
        :param income: amount of money to change
        :param method: 'plus' or 'minus' - add or subtract
        :return: Log message
        """
        if method == 'plus':
            balance = self.get_balance(card) + income
        elif method == 'minus':
            balance = self.get_balance(card) - income
        self.cur.execute("""
                         UPDATE card
                         SET balance = {balance} 
                         WHERE number = {card}"""
                         .format(balance=balance, card=card))
        self.conn.commit()
        return "Income was added!\n"

    def do_transfer(self, card_from: str, card_to: str, how_much: int):
        """
        Does money transfer from one card to another
        :param card_from: Card number from
        :param card_to: Card number to
        :param how_much: Amount of money
        :return: Log message
        """
        balance = self.get_balance(card_from)
        if how_much > balance:
            return "Not enough money!\n"
        else:
            self.balance_change(card_to, how_much, 'plus')
            self.balance_change(card_from, how_much, 'minus')
            return "Success!\n"

    def close_account(self, card: str):
        """
        Closes account
        :param card: Card number
        :return: Log message
        """
        self.cur.execute("""
                         DELETE FROM card
                         WHERE number = {card}"""
                         .format(card=card))
        self.conn.commit()
        print("The account has been closed!\n")

    def logout(self, card: str):
        """
        Logs out the account being logined
        :param card: Card number
        :return: Log message
        """
        print('You have successfully logged out!\n')
        self.accounts_logged_in[card]['login'] = 0
