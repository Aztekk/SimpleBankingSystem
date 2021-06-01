from bank import Bank

bank = Bank()

condition = 1
while condition != 0:
    print("1. Create an account\n"
          "2. Log into account\n"
          "0. Exit\n")
    condition = int(input())
    if condition == 1:
        bank.create_account()
    elif condition == 2:
        print('Enter your card number:')
        outer_card = input()
        print('Enter your PIN:')
        outer_pin = input()
        bank.login(outer_card, outer_pin)
        if outer_card in bank.accounts_logged_in:
            if bank.accounts_logged_in[outer_card]['login'] == 1:
                while bank.accounts_logged_in[outer_card]['login'] == 1:
                    print("1. Balance\n"
                          "2. Add income\n"
                          "3. Do transfer\n"
                          "4. Close account\n"
                          "5. Log out\n"
                          "0. Exit\n")
                    query = int(input())
                    if query == 1:
                        money = bank.get_balance(outer_card)
                        print("Balance: {m}\n".format(m=money))
                    elif query == 2:
                        print("Enter income:\n")
                        money = int(input())
                        bank.balance_change(outer_card, money, 'plus')
                        print("Income was added!\n")
                    elif query == 3:
                        print("Transfer\n"
                              "Enter card number:")
                        where_to = input()
                        if not bank.luhn_pass(where_to):
                            print("Probably you made a mistake in the card number. Please try again!\n")
                        elif not bank.number_in_base(where_to):
                            print("Such a card does not exist.\n")
                        else:
                            print("Enter how much money you want to transfer:")
                            money = int(input())
                            print(bank.do_transfer(outer_card, where_to, money))
                    elif query == 4:
                        bank.close_account(outer_card)
                        break
                    elif query == 5:
                        bank.logout(outer_card)
                        break
                    elif query == 0:
                        condition = 0
                        print('Bye!')
                        break
                    else:
                        print('Choose one of the following options!\n')
    elif condition == 0:
        print('Bye!')
        break

    else:
        print('Choose one of the following options!\n')
