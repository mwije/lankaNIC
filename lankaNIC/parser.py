import re
from .exceptions import InvalidNICError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class NICParser:
    def __init__(self, nic_number: str = ""):
        self._nic_old_regex = re.compile(r"^(\d{2})(\d{3})(\d{4})([VX])$")
        self._nic_new_regex = re.compile(r"^(\d{4})(\d{3})(\d{5})$")
        if nic_number:
            self.nic_number = nic_number

    @property
    def nic_number(self):
        """Getter for the NIC number."""
        return self._nic_number

    @nic_number.setter
    def nic_number(self, value: str):
        """Setter for the NIC number with validation."""
        if not isinstance(value, str):
            raise ValueError("NIC number must be a string")
        self._nic_number = value.strip()
        self.parse()

    @property
    def is_valid(self):
        """Returns whether the NIC number is valid or not, computes on demand"""
        return not self.format == None

    @property
    def sex(self):
        return self._sex

    @property
    def voting(self):
        return self._voting

    @property
    def birth_day(self):
        return self._dob

    @property
    def age(self):
        delta = relativedelta(datetime.now(), self._dob)
        return f"{delta.years} years, {delta.months} months, {delta.days} days"

    @property
    def next_birth_day(self):
        today = datetime.now()
        this_year_birthday = self._dob.replace(year=today.year)

        if this_year_birthday < today:
            next_birthday = this_year_birthday.replace(year=today.year + 1)
            days_to = (next_birthday - today).days
            return f"{days_to} days"
        elif this_year_birthday > today:
            days_to = (this_year_birthday - today).days
            return f"{days_to} days"
        else:
            return "Today!"

    @property
    def format(self):
        return self._format

    @property
    def is_voting(self):
        return self._voting

    @property
    def serial(self):
        return self._serial

    @property
    def checkdigit(self):
        return self._checkdigit

    def parse(self):
        nic_number = self._nic_number
        if self._nic_old_regex.match(nic_number):
            self._format = "Pre-2016"
            if int(nic_number[:2])<16:
                nic_number = "20" + nic_number
            else:
                nic_number = "19" + nic_number
        elif self._nic_new_regex.match(nic_number):
            self._format = "Post-2016"
        else:
            self._format = None
            raise InvalidNICError(f"Invalid NIC: {nic_number}")

        # Year
        birth_year = nic_number[:4]
        day_of_year = int(nic_number[4:7])

        # Sex
        if day_of_year>500:
            day_of_year-=500
            self._sex = "Female"
        else:
            self._sex = "Male"

        # Birth Day
        self._dob = datetime.strptime(f"{birth_year} {day_of_year}", "%Y %j")

        # Voting Elligibility
        self._voting = nic_number[-1]
        d=0
        match self._voting:
            case "V":
                voting = True
            case "X":
                voting = False
            case default:
                voting = None
                d=1
        
        # Other Digits
        self._serial = nic_number[7:-2+d]
        self._checkdigit = nic_number[-2+d]

