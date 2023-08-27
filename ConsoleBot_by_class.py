from collections import UserDict
from collections.abc import Iterator
import time
from datetime import datetime

class AddressBook(UserDict):
    '''The only Address book'''
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(AddressBook, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        super(AddressBook, self).__init__()
        self.data = {}
        self.cache = []
        self.idx_sheet = [0, 2]

    def add_record(self, record):
        '''Add some contact'''
        key = record.name.value
        self.data[key] = record

    def show_all(self):
        '''Show all contacts'''
        self.cache = []
        for username, rec in self.items():
            days_to_birthday = rec.days_to_birthday()\
                    if rec.days_to_birthday() else '------'

            if rec.phones:
                self.cache.append('|{:^15}|{:^15}|{:^16}|\n'.format(
                            username.title(),
                            rec.phones[0].value,
                            days_to_birthday
                            ))
                if len(rec.phones) == 1:
                    continue

                for num in rec.phones[1:]:
                    self.cache.append('|{:^15}|{:^15}|{:^16}|\n'.format(
                        '', num.value, '------'
                        ))
            else:
                self.cache.append('|{:^15}|{:^15}|{:^16}|\n'.format(
                            username, ' ', days_to_birthday
                            ))


    def __next__(self):
        if self.idx_sheet[0] >= self.idx_sheet[1]:
            self.idx_sheet = [0, 2]
            raise StopIteration
        sheet = '|{:^15}|{:^15}|{:^16}|\n'.format(
                                'Username',
                                'Phone',
                                'Days to birthday'
                                )
        for string in self.cache[self.idx_sheet[0] : self.idx_sheet[1]]:
            sheet += string

        self.idx_sheet.pop(0)
        if (self.idx_sheet[0] + 2) <= len(self.cache):
            self.idx_sheet.append(self.idx_sheet[0] + 2)
            
        else: self.idx_sheet.append(len(self.cache))
        return sheet

class AddressBookIter:
    '''Seting up the Iterator for AddressBook'''
    def __iter__(self) -> Iterator:
        return ab

class Record:
    def __init__(self, name, phone=None, birthday=None) -> None:
        self.name = name
        self.birthday = birthday
        self.phones = []
        if phone:
            if phone not in self.phones:
                self.phones.append(phone)

    def add(self, phone):
        self.phones.append(phone)

    def edit(self, phone_to_edit, new_phone):
        pass

    def days_to_birthday(self):
        if self.birthday.value:
            now = datetime.now()
            birthday = self.birthday.value
            next_birthday = birthday.replace(year=now.year)
            if next_birthday < now:
                next_birthday = next_birthday.replace(year=next_birthday.year + 1)
            return next_birthday.toordinal() - now.toordinal()


class Field:
    pass
    # def __init__(self) -> None:
    #     self.value = {}
    # def __setattr__(self, __name: str, __value: Any) -> None:
    #     self.value[__name] = __value


class Name(Field):
    def __init__(self, name) -> None:
        self.value = name


class Birthday(Field):
    def __init__(self, birthday) -> None:
        self.value = birthday

class Phone(Field):
    def __init__(self, phone) -> None:
        self.value = phone


class UsernameError(LookupError):
    '''Username not found!'''
class CommandError(LookupError):
    '''Undefined command'''
class DateError(LookupError):
    '''Unsupported date format'''    


def input_error(handler: tuple) -> str:
    '''Return input error'''
    errors = {
        1: 'Enter valid command!',
        2: 'Username not found',
        3: 'Enter valid username and(or) phone (phone must contain only digits)',
        4: 'Number not found',
        5: 'Please enter date using format "YYYY-MM-DD"'
    }
    def trying(command: str, args) -> str:
        try:
            answer = handler(command, args)
        except UsernameError:
            return errors[2]
        except ValueError:
            return errors[4]
        except IndexError:
            return errors[3]
        except CommandError:
            return errors[1]
        except KeyError:
            return errors[2]
        except DateError:
            return errors[5]
        return answer
    return trying

@input_error
def handler(command: str, args) -> str:
    '''Handle commands'''
    global ab

    def greet():
        return 'Hello!\nHow can I help you?'


    def add(name: str, phone=None, birthday=None) -> str:
        '''Add user number and/or birthday into database'''
        try:
            if birthday:
                birthday = datetime.strptime(birthday, '%Y-%m-%d')
        except ValueError as err:
            raise DateError from err

        if name in ab.keys():
            if phone:
                phone = Phone(phone)
                ab[name].add(phone)
            if birthday:
                birthday = Birthday(birthday)
                ab[name].birthday = birthday
            return 'Done'

        name = Name(name)
        if phone:
            phone = Phone(phone)
        birthday = Birthday(birthday)
        rec = Record(name, phone, birthday)
        ab.add_record(rec)
        return 'Done'


    def change(name, old_number, new_number) -> str:
        '''Change user number'''

        if name not in ab.keys():
            raise UsernameError

        for phone in ab[name].phones:
            if phone.value == old_number:
                phone.value = new_number
                return 'Done'

        raise ValueError

    def show(name: str) -> str:
        '''Show User phone.\n
        If key: 'all' - show all contacts'''

        if name == 'all':
            ab.show_all()
            return ab_iter

        days_to_birthday = '------'
        if ab[name].birthday.value:
            days_to_birthday = ab[name].days_to_birthday()

        text = '|{:^15}|{:^15}|{:^16}|\n'.format(
                                'Username',
                                'Phone',
                                'Days to birthday'
                            )
        for phone in ab[name].phones:
            text += '|{:^15}|{:^15}|{:^16}|'.format(
                                ab[name].name.value,
                                phone.value,
                                days_to_birthday
                            )
        return text

    if command == 'hello':
        return greet()
    elif command == 'add':
        return add(args[0], args[1], args[2])
    elif command == 'change':
        return change(args[0], args[1], args[2])
    elif command == 'phone':
        return show(args[0])
    elif command == 'show':
        return show(args[0])
    raise CommandError

def parser(raw_input: str) -> str|tuple[str]:
    '''Returns (command, name, number, birthday)'''
    raw_input = str(raw_input)
    if raw_input == 'good bye' or\
       raw_input == 'close' or\
       raw_input == 'exit' or\
       raw_input == 'quit':
        print('Good bye!')
        time.sleep(3)
        return 'break'

    user_input = raw_input.split(' ')
    if len(user_input) < 2:
        return 'error'
    command = user_input[0]
    name = user_input[1]
    number = None
    birthday = None

    if len(user_input) > 2:
        for inp in user_input[2:]:
            if inp.isnumeric():
                number = inp
                continue
            birthday = inp

    return (command, name, number, birthday)

def main() -> None:
    """Main cycle"""
    index = -1
    while True:
        # command = parser(input().lower())

        command = input()

        if command == '':
            index += 1
            test = [
                'add nick 15952124',
                'add nick 1992-1-5',
                'show all',
                'show nick',
                'add nancy 159648 1552-4-7',
                'add nana 5934 2002-4-7',
                'add nency 1594648 1552-4-7',
                'add nata 59314 2002-4-7',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                    ]
            print(test[index])
            command = test[index]
        command = parser(command.lower())
        if command == 'break':
            break
        result = handler(command[0], command[1:])

        if isinstance(result, AddressBookIter):
            for sheet in result:
                print(sheet)
                break
        else:
            print(result)


if __name__ == "__main__":
    ab = AddressBook()
    ab_iter = AddressBookIter()
    main()
