import os
from enum import Enum, auto

FILE_PATH = os.path.join(os.getcwd(),"values.env")

def decorator_for_show_func (func) :
  def wrapper (*args, **kwargs) :
    print()
    func(*args, **kwargs)
  
  return wrapper

def str_form (str_list) :
  length_of_str_list = len(str_list)
  padding_size = [10 for _ in range(length_of_str_list - 1)]
  padding_size.insert(0, 20)
  str_format = ""
  for idx in range(length_of_str_list) :
    each = str_list[idx]
    str_format += each + ' ' * (padding_size[idx] - calculate_length_of_str(each))
  str_format += '\n'

  return str_format

def calculate_length_of_str (str_input) :
  length_of_str_input = 0
  for char in str_input : 
    if '\uAC00' <= char <= '\uD7AF' :
      length_of_str_input += 2
    else : 
      length_of_str_input += 1
  
  return length_of_str_input


class Status (Enum) :
  normal = auto()

  cleaning_room = "생활관 청소"
  seperating_trash_each_room = "생활관 분리수거"
  seperating_trash = "분리수거"

  vacation = "휴가"
  vacation_but_coming_this_week = "휴가복귀"
  dispatch = "파견"
  discharge = "전역"
  sleepover = "외박"


class RoomMembers :
    
  def __init__ (self, file_path) :
    self.file_contents = self.read_file_contents(file_path)
    self.members_status = {}
    self.members_map = self.get_members_map()

    self.excluded_members = self.members_map["excluded_members"]
    self.excluded_but_lottery_members = self.members_map["excluded_but_lottery_members"]
    self.cleaning_members_before_week = self.members_map["cleaning_members_before_week"]

    self.cleaning_members = {}
    self.cleaning_members_list = []

  def read_file_contents(self, file_path) :
    with open(file_path, 'r') as file :
      contents = file.readlines()
    return contents
  
  def get_members_map (self) :
    members_map = {}

    for idx in range(4) : 
      room_number = "room" + str(idx + 1)
      members_map[room_number] = [i.strip() for i in self.file_contents[idx].split(':')[1].split(',')]
      self.set_status(members_map[room_number], Status.normal)

    raw_excluded_members = ""

    special_reasoned_members = []
    for idx in range(4) : 
      raw_members_tmp = self.file_contents[idx + 11].split(':')[1]
      special_reasoned_members.insert(idx, raw_members_tmp)
      if raw_members_tmp.strip() != '' : 
        raw_excluded_members += raw_members_tmp + ','
        
    vacation_members = special_reasoned_members[0]
    dispatch_members = special_reasoned_members[1]
    discharge_members = special_reasoned_members[2]
    sleepover_members = special_reasoned_members[3]

    self.set_status(vacation_members, Status.vacation)
    self.set_status(dispatch_members, Status.dispatch)
    self.set_status(discharge_members, Status.discharge)
    self.set_status(sleepover_members, Status.sleepover)

    
    members_map["seperating_trash"] = {}
    for idx in range(4) : 
      each_excluded_members = self.file_contents[idx + 16].split(':')[1].strip()
      members_map["seperating_trash"]["room" + str(idx + 1)] = each_excluded_members
      raw_excluded_members += each_excluded_members + ',' 

      self.members_status[each_excluded_members] = Status.seperating_trash
    
    members_map["excluded_members"] = [i.strip() for i in raw_excluded_members[:-1].split(',')]
    members_map["excluded_but_lottery_members"] = [i.strip() for i in self.file_contents[21].split(':')[1].split(',')]
    for each in members_map["excluded_but_lottery_members"] :
      self.set_status(each, Status.vacation_but_coming_this_week)

    members_map["cleaning_members_before_week"] = {}
    for idx in range(4) :
      members_map["cleaning_members_before_week"]["room" + str(idx + 1)] = { "cleaning_room" : self.file_contents[idx + 6].split(':')[1].split(',')[0].strip(), "seperating_trash_each_room" : self.file_contents[idx + 6].split(':')[1].split(',')[1].strip() }

    return members_map

  def set_status (self, member, status) :
    if type(member) is list : 
      for each in member :
        if each.strip() != '' :
          self.members_status[each] = status
    else :
      if type(member) is str :
        member = member.split(',')
        if type(member) is list :
          for each in member :
            if each.strip() != '' :
              self.members_status[each.strip()] = status
        else :
          member = member.strip()
          if member != '' :
            self.members_status[member] = status

  def get_next_cleaning_members (self) :
    cleaning_members = {}
    for idx in range(4) :
      room_number = "room" + str(idx + 1)
      cleaning_members[room_number] = {}
      cleaning_members[room_number] = self.get_next_members(room_number)

      cleaning_members[room_number]["seperating_trash"] = self.members_map["seperating_trash"][room_number]

    self.cleaning_members = cleaning_members
    self.cleaning_members_list = [val for each in cleaning_members.values() for val in each.values()]
    return cleaning_members

  def get_next_members (self, room_number) : 
    room_members = self.members_map[room_number]
    room_members_length = len(room_members)

    before_work_member = self.members_map["cleaning_members_before_week"][room_number]
    before_cleaning_room_member = before_work_member["cleaning_room"]
    before_seperating_trash_each_room_member = before_work_member["seperating_trash_each_room"]

    excluded_members = self.excluded_members
    before_cleaning_room_member_idx = room_members.index(before_cleaning_room_member)
    before_seperating_trash_each_room_member_idx = room_members.index(before_seperating_trash_each_room_member)

    next_cleaning_room_member = None
    count = 0
    idx = before_cleaning_room_member_idx + 1
    if idx == room_members_length : 
      idx = 0

    while(not count == room_members_length) :
      this_member = room_members[idx]
      if this_member not in excluded_members :
        if next_cleaning_room_member is None : 
          next_cleaning_room_member = this_member
        else :
          if this_member != before_seperating_trash_each_room_member :
            self.members_status[next_cleaning_room_member] = Status.cleaning_room
            self.members_status[this_member] = Status.seperating_trash_each_room
            return {"cleaning_room" : next_cleaning_room_member, "seperating_trash_each_room" : this_member}

      if (idx + 1) == room_members_length :
        idx = 0
      else :
        idx += 1
      count += 1

    return "error"

  def get_lottery_members (self) :
    lottery_members = {}
    for idx in range(4) :
      room_number = "room" + str(idx + 1)
      lottery_members[room_number] = self.get_lottery_members_each_room(room_number)

    return lottery_members

  def get_lottery_members_each_room (self, room_number) :
    room_members = self.members_map[room_number]
    excluded_members = self.members_map["excluded_members"]
    excluded_but_lottery_members = self.members_map["excluded_but_lottery_members"]
    cleaning_members_list = self.cleaning_members_list

    return list(filter(lambda each : each not in cleaning_members_list and ((each in excluded_members) is (each in excluded_but_lottery_members)) , room_members))

  @decorator_for_show_func
  def show_status (self) :
    print("전체인원 현황")
    for idx in range(4) :
      room_number = "room" + str(idx + 1)
      before_cleaning_members = self.cleaning_members_before_week[room_number]
      members = self.members_map[room_number]
      print(str(idx + 1) + "생활관 : ", end = '')
      for each in members :
        status = self.members_status[each]
        print(each, end = '')

        if each == before_cleaning_members["cleaning_room"] : 
          print("(이전 생활관 청소)", end = '')
        if each == before_cleaning_members["seperating_trash_each_room"] :
          print("(이전 생활관 분리수거)", end = '')

        if status == Status.normal :
          print(', ', end = '')
        else :
          print('(' + self.members_status[each].value + "), ", end = '')
      print(end = "\n\n")
    
  def get_before_week_cleaning_members_by_area (self) :
    cleaning_members_before_week = self.cleaning_members_before_week
    before_week_cleaning_members_by_area = {}
    for idx in range(4) :
      room_number = "room" + str(idx + 1)
      before_week_cleaning_members_by_area["cleaning_room"] = cleaning_members_before_week[room_number]["cleaning_room"]
      before_week_cleaning_members_by_area["seperating_trash_each_room"] = cleaning_members_before_week[room_number]["seperating_trash_each_room"]

    return before_week_cleaning_members_by_area

  @decorator_for_show_func
  def show_summary (self) :
    room_numbers = [str(idx + 1) + "생활관" for idx in range(4)]
    room_numbers.insert(0, '')

    cleaning_room = ["생활관 청소"]
    seperating_trash_each_room = ["생활관 분리수거"]
    seperating_trash = ["분리수거"]
    cleaning_members = self.get_next_cleaning_members()
    for idx in range(4) :
      room_members = cleaning_members["room" + str(idx + 1)]
      cleaning_room.insert(idx + 1, room_members["cleaning_room"])
      seperating_trash_each_room.insert(idx + 1, room_members["seperating_trash_each_room"])
      seperating_trash.insert(idx + 1, room_members["seperating_trash"])

    str_output = ""
    str_output += str_form(room_numbers)
    str_output += str_form(cleaning_room)
    str_output += str_form(seperating_trash_each_room)
    str_output += str_form(seperating_trash)

    print(str_output)

  @decorator_for_show_func
  def show_lottery_members (self) :
    lottery_members = self.get_lottery_members()

    print("제비뽑기 인원")
    for idx in range(4) :
      room_number = "room" + str(idx + 1)
      print(str(idx + 1) + "생활관 : " +  str(lottery_members[room_number]))


if __name__ == "__main__" :
  room_members = RoomMembers(FILE_PATH)

  room_members.show_summary()
  room_members.show_lottery_members()
  room_members.show_status()