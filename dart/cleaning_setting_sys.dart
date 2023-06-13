import 'dart:io';

const String INPUT_FILE_PATH = 'values.env';
const String OUTPUT_FILE_PATH = 'output.env';

typedef void ShowFunc();

void decoratorForShowFunc(ShowFunc func) {
  print('');
  func();
}

String strForm(List<String> strList) {
  int lengthOfStrList = strList.length;
  List<int> paddingSize = List<int>.filled(lengthOfStrList - 1, 10);
  paddingSize.insert(0, 20);
  String strFormat = '';
  for (int idx = 0; idx < lengthOfStrList; idx++) {
    String each = strList[idx];
    strFormat += each + ' ' * (paddingSize[idx] - calculateLengthOfStr(each));
  }
  strFormat += '\n';

  return strFormat;
}

int calculateLengthOfStr(String strInput) {
  int lengthOfStrInput = 0;
  for (int i = 0; i < strInput.length; i++) {
    String char = strInput[i];
    if ('\uAC00' <= char && char <= '\uD7AF') {
      lengthOfStrInput += 2;
    } else {
      lengthOfStrInput += 1;
    }
  }

  return lengthOfStrInput;
}

enum Status {
  normal,
  cleaningRoom,
  seperatingTrashEachRoom,
  seperatingTrash,
  vacation,
  vacationButComingThisWeek,
  dispatch,
  discharge,
  sleepover,
}

class RoomMembers {
  late List<String> fileContents;
  Map<String, dynamic> membersStatus = {};
  late Map<String, dynamic> membersMap;
  late List<String> excludedMembers;
  late List<String> excludedButLotteryMembers;
  late Map<String, dynamic> cleaningMembersBeforeWeek;
  late Map<String, dynamic> cleaningMembers;
  late List<dynamic> cleaningMembersList;

  RoomMembers(String filePath) {
    fileContents = readFileContents(filePath);
    membersMap = getMembersMap();
    excludedMembers = membersMap['excluded_members'];
    excludedButLotteryMembers = membersMap['excluded_but_lottery_members'];
    cleaningMembersBeforeWeek = membersMap['cleaning_members_before_week'];
    cleaningMembers = {};
    cleaningMembersList = [];

    getMembersStatus(membersMap);
  }

  List<String> readFileContents(String filePath) {
    File file = File(filePath);
    return file.readAsLinesSync();
  }

  void writeFileContents(String contents, String filePath) {
    File file = File(filePath);
    file.writeAsStringSync(contents);
  }

  Map<String, dynamic> getMembersMap() {
    Map<String, dynamic> membersMap = {};

    for (int idx = 0; idx < 4; idx++) {
      String roomNumber = 'room${idx + 1}';
      membersMap[roomNumber] =
          fileContents[idx].split(':')[1].split(',').map((e) => e.trim()).toList();
      setMembersStatus(membersMap[roomNumber], Status.normal);
    }

    String rawExcludedMembers = '';

    List<String> specialReasonedMembers = [];
    for (int idx = 0; idx < 4; idx++) {
      String rawMembersTmp = fileContents[idx + 11].split(':')[1];
      specialReasonedMembers.insert(idx, rawMembersTmp);
      if (rawMembersTmp.trim() != '') {
        rawExcludedMembers += rawMembersTmp + ',';
      }
    }

    String vacationMembers = specialReasonedMembers[0];
    String dispatchMembers = specialReasonedMembers[1];
    String dischargeMembers = specialReasonedMembers[2];
    String sleepoverMembers = specialReasonedMembers[3];

    membersMap['vacation_members'] = vacationMembers.split(',').map((e) => e.trim()).toList();
    membersMap['dispatch_members'] = dispatchMembers.split(',').map((e) => e.trim()).toList();
    membersMap['discharge_members'] = dischargeMembers.split(',').map((e) => e.trim()).toList();
    membersMap['sleepover_members'] = sleepoverMembers.split(',').map((e) => e.trim()).toList();
    membersMap['excluded_members'] = rawExcludedMembers.split(',').map((e) => e.trim()).toList();
    membersMap['excluded_but_lottery_members'] = membersMap['excluded_members']
        .where((element) => !excludedButLotteryMembers.contains(element))
        .toList();
    return membersMap;
  }

  void setMembersStatus(List<String> members, Status status) {
    for (String member in members) {
      membersStatus[member] = status;
    }
  }

  void getMembersStatus(Map<String, dynamic> membersMap) {
    for (String room in membersMap.keys) {
      setMembersStatus(membersMap[room], Status.normal);
    }

    setMembersStatus(membersMap['vacation_members'], Status.vacation);
    setMembersStatus(membersMap['dispatch_members'], Status.dispatch);
    setMembersStatus(membersMap['discharge_members'], Status.discharge);
    setMembersStatus(membersMap['sleepover_members'], Status.sleepover);
  }

  void printMembersStatus() {
    List<String> membersStatusList = [];
    membersStatus.forEach((key, value) {
      membersStatusList.add('$key: $value');
    });

    print(membersStatusList.join('\n'));
  }

  void calculateCleaningMembers() {
    DateTime now = DateTime.now();
    DateTime oneWeekAgo = now.subtract(Duration(days: 7));
    cleaningMembersBeforeWeek.forEach((member, lastCleaningDate) {
      DateTime lastDate = DateTime.parse(lastCleaningDate);
      if (lastDate.isBefore(oneWeekAgo)) {
        cleaningMembers[member] = lastCleaningDate;
        cleaningMembersList.add(member);
      }
    });
  }

  String getNextCleaningMember() {
    if (cleaningMembersList.isEmpty) {
      calculateCleaningMembers();
    }

    if (cleaningMembersList.isEmpty) {
      return 'No member needs to clean this week.';
    } else {
      String nextMember = cleaningMembersList.first;
      cleaningMembersList.removeAt(0);
      return nextMember;
    }
  }

  void showRoomStatus() {
    print('Room Members:');
    membersMap.forEach((room, members) {
      print('Room $room: ${members.join(', ')}');
    });

    decoratorForShowFunc(() {
      print('Excluded Members: ${excludedMembers.join(', ')}');
      print('Excluded but Lottery Members: ${excludedButLotteryMembers.join(', ')}');
    });

    decoratorForShowFunc(() {
      print('Cleaning Members Before Week:');
      cleaningMembersBeforeWeek.forEach((member, lastCleaningDate) {
        print('$member: $lastCleaningDate');
      });
    });

    decoratorForShowFunc(() {
      print('Cleaning Members:');
      cleaningMembers.forEach((member, lastCleaningDate) {
        print('$member: $lastCleaningDate');
      });
    });

    decoratorForShowFunc(() {
      print('Members Status:');
      printMembersStatus();
    });
  }

  void saveMembersStatus() {
    List<String> outputLines = [];
    membersMap.forEach((room, members) {
      outputLines.add('Room $room: ${members.join(',')}');
    });

    decoratorForSaveFunc(() {
      outputLines.add('Excluded Members: ${excludedMembers.join(',')}');
      outputLines.add('Excluded but Lottery Members: ${excludedButLotteryMembers.join(',')}');
    });

    decoratorForSaveFunc(() {
      outputLines.add('Cleaning Members Before Week:');
      cleaningMembersBeforeWeek.forEach((member, lastCleaningDate) {
        outputLines.add('$member: $lastCleaningDate');
      });
    });

    decoratorForSaveFunc(() {
      outputLines.add('Cleaning Members:');
      cleaningMembers.forEach((member, lastCleaningDate) {
        outputLines.add('$member: $lastCleaningDate');
      });
    });

    decoratorForSaveFunc(() {
      outputLines.add('Members Status:');
      membersStatus.forEach((member, status) {
        outputLines.add('$member: $status');
      });
    });

    File('members_status.txt').writeAsStringSync(outputLines.join('\n'));
    print('Members status saved to members_status.txt.');
  }
}

void main() {
  print('===== Welcome to Room Management System! =====');
  RoomManagement roomManagement = RoomManagement();

  bool exitFlag = false;
  while (!exitFlag) {
    print('\nPlease select an action:');
    print('1. Show room status');
    print('2. Assign cleaning member');
    print('3. Save members status');
    print('4. Exit');

    String input = stdin.readLineSync();
    switch (input) {
      case '1':
        roomManagement.showRoomStatus();
        break;
      case '2':
        String nextCleaningMember = roomManagement.getNextCleaningMember();
        print('The next cleaning member is: $nextCleaningMember');
        break;
      case '3':
        roomManagement.saveMembersStatus();
        break;
      case '4':
        exitFlag = true;
        break;
      default:
        print('Invalid input. Please try again.');
    }
  }

  print('Thank you for using the Room Management System. Goodbye!');
}
