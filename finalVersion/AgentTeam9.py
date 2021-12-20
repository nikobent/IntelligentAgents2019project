from owlready2 import *
import random


class Agent():
    """here follows the agent class, below there is the description for every internal function"""
    def __init__(self ,md_crs, friends, bd_lec, bd_rms, bd_crs, exam,bd_topics ,day):
        self.courses_in_mind = md_crs
        self.friends = friends
        self.bad_topics = bd_topics
        self.bad_lecturers = bd_lec
        self.bad_courses = bd_crs
        self.bad_day = day
        self.bad_rms = bd_rms
        self.pref_exam =exam
        pass
    """1. utility: Input:schedule, output: utility score
        description: examine each course from the schedule, assign it a utility score based on the preferences he fullfils or not (weights assigned into a dictionary)
        at the end each courses score is summed together which is the output"""
    def utility(self, schedule):
        weigths = {'noPC': 0.5,'noPT':0.6,'noPL':0.7,'noPD':0.75,'noRM':0.85,'CIM':2,'FW':1.5, 'EX':1.4}
        sum = 0
        for i in range (4):
            for j in range(2):
                score = 1
                if schedule[i][j] in self.courses_in_mind:
                    score = score * weigths['CIM']
                if schedule[i][j] in list(onto.FRIENDS_COURSE.instances()):
                    score = score * weigths['FW']
                if schedule[i][j] in list(onto.EXAM_COURSE.instances()):
                    score = score * weigths['EX']
                if schedule[i][j] in list(onto.BAD_COURSE.instances()):
                    score = score * weigths['noPC']
                if schedule[i][j] in list(onto.BAD_TOPIC_COURSE.instances()):
                    score = score * weigths['noPT']
                if schedule[i][j] in list(onto.BAD_LECTURERS_COURSE.instances()):
                    score = score * weigths['noPL']
                if schedule[i][j] in list(onto.BAD_DAY_COURSE.instances()):
                    score = score * weigths['noPD']
                if schedule[i][j] in list(onto.BAD_RM_COURSE.instances()):
                    score = score * weigths['noRM']
                sum = sum + score
        return sum
    """Input: list with the three utility scores of the created schedules, output: the index of the best utility score
    description: here is the comparison of all the utility scores, the biggest utility sccore is the schedule for our new student"""
    def decision_maker(self, utilities):
        mx = max(utilities)
        for i in range(3):
            if utilities[i] == mx:
                return i
    """description: the function of the system that all the other internal functions are called
    first it calls the creation_list() function to gather all the lists that help us with the creation of the schedules,
    then it creates the schedules with the function schedules(),
    then it creates a list with the utility scores of these schedules (utility() function),
    then calls the decision_maker() to find the best schedule
    and at the end this Schedule is printed to the user"""
    def create_schedule(self):
        self.creation_lists()
        self.schedules = self.schedules()

        utility_scores = []
        for i in self.schedules:
            utility_scores.append(self.utility(i))
        winner = self.decision_maker(utility_scores)
        sch = self.schedules[winner]
        print("Hey {}, your schedule is the following with utility score {}:\n".format(student.person_name,utility_scores[winner]))
        for i in range(4):
            print ("Period {}:\n".format(i+1))
            for j in range(2):
                print(sch[i][j].course_name)
                print("\n")
        print("Have a good academic year!")
    """description: here all the lists that we are going to use are created. this lists include courses that fullfill some or all of the user's preferences,
    First we created some list of courses using reasoning, for the other lists this was unsuccesful, because the ontology did not support the Not-syntax element
    and proceeded to create them using a more pythonic way of doing it. Each list has a description before its creation for a better understanding"""
    def creation_lists(self):
        with onto:
            # new construct with the courses that the student doesn't mind taking
            class COURSE(Thing):
                equivalent_to = [
                    (onto.Period1C | onto.Period2C | onto.Period3C | onto.Period4C)]
            class BAD_DAY_COURSE(Thing):
                equivalent_to = [
                    onto.COURSE & (onto.taughtAtDay.value(day))]
            # the courses that user's friends chose"""
            class FRIENDS_COURSE(Thing):
                equivalent_to = [onto.COURSE & onto.isTakenBy.some(onto.isFriendWith.value(student))]
            class BAD_LECTURERS_COURSE(Thing):
                equivalent_to = [
                    onto.COURSE & onto.isTaughtBy.some(onto.Lecturer & (onto.blacklisted_by.value(student)))]
            # Courses of unwanted topic
            class BAD_TOPIC_COURSE(Thing):
                equivalent_to = [onto.COURSE & onto.hasTopic.some(onto.Topic & (onto.topic_displeases.value(student)))]
            # Courses of unwanted RM
            class BAD_RM_COURSE(Thing):
                equivalent_to = [
                    onto.COURSE & onto.includesRM.some(onto.RM & (onto.rm_displeases.value(student)))]
            class BAD_COURSE(Thing):
                equivalent_to =[onto.COURSE & onto.courseBlaclistedBy.value(student)]
            class MAN_COURSE(Thing):
                equivalent_to = [onto.COURSE & onto.isMandatory.value(onto.MYES)]
            if self.pref_exam == onto.EYES:
                class EXAM_COURSE(Thing):
                    equivalent_to = [onto.COURSE & onto.hasExam.value(onto.EYES)]
            elif self.pref_exam == onto.ENO:
                class EXAM_COURSE(Thing):
                    equivalent_to = [onto.COURSE & onto.hasExam.value(onto.ENO)]
            sync_reasoner(onto, infer_property_values=True)
        #COURSES THAT RESPECT ALL
        best_courses = []
        for cor in self.courses_in_mind:
            if cor in list(onto.FRIENDS_COURSE.instances()) and cor in list(onto.EXAM_COURSE.instances()) and cor not in list(onto.BAD_LECTURERS_COURSE.instances()) and cor not in list(onto.BAD_DAY_COURSE.instances()) and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                best_courses.append(cor)
        self.best_courses = best_courses
        #courses that escape all the negative preferences, but our student may not have them in mind. Still the exam preference is matched and friends courses also
        still_good_courses = []
        for cor in list(onto.COURSE.instances()):
            if cor in list(onto.FRIENDS_COURSE.instances()) and cor in list(onto.EXAM_COURSE.instances()) and cor not in list(onto.BAD_LECTURERS_COURSE.instances()) and cor not in list(onto.BAD_DAY_COURSE.instances()) and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                still_good_courses.append(cor)
        self.still_good_courses = still_good_courses
        #courses that escape all the negative preferences, but our student may not have them in mind AND we don't care if our friends have picked them. Still the exam preference is  matched
        still_good_courses_nf= []
        for cor in list(onto.COURSE.instances()):
            if cor in list(onto.EXAM_COURSE.instances()) and cor not in list(onto.BAD_LECTURERS_COURSE.instances()) and cor not in list(onto.BAD_DAY_COURSE.instances()) and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                still_good_courses_nf.append(cor)
        self.still_good_courses_nf = still_good_courses_nf
        #courses that escape all the negative preferences, but our student may not have them in mind AND we don't care about exam preference. Friends courses are matched
        still_good_courses_ne= []
        for cor in list(onto.COURSE.instances()):
            if cor in list(onto.FRIENDS_COURSE.instances()) and cor not in list(onto.BAD_LECTURERS_COURSE.instances()) and cor not in list(onto.BAD_DAY_COURSE.instances()) and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                still_good_courses_ne.append(cor)
        self.still_good_courses_ne = still_good_courses_ne
        #courses that escape all negative preferences
        non_bad = []
        for cor in list(onto.COURSE.instances()):
            if  cor not in list(onto.BAD_LECTURERS_COURSE.instances()) and cor not in list(onto.BAD_DAY_COURSE.instances()) and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                non_bad.append(cor)
        self.non_bad = non_bad
        #non negative courses but we don't care about the day
        non_bad_nd = []
        for cor in list(onto.COURSE.instances()):
            if  cor not in list(onto.BAD_LECTURERS_COURSE.instances())  and cor not in list(onto.BAD_RM_COURSE.instances()) and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                non_bad_nd.append(cor)
        self.non_bad_nd = non_bad_nd
        #non negative courses but we don't care about the day and rm
        non_bad_ndrm = []
        for cor in list(onto.COURSE.instances()):
            if  cor not in list(onto.BAD_LECTURERS_COURSE.instances())  and cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                non_bad_ndrm.append(cor)
        self.non_bad_ndrm = non_bad_ndrm
        #non negative courses but we don't care about the day, rm and lecturer
        non_bad_ndrmle = []
        for cor in list(onto.COURSE.instances()):
            if  cor not in list(onto.BAD_TOPIC_COURSE.instances()) and cor not in list(onto.BAD_COURSE.instances()):
                non_bad_ndrmle.append(cor)
        self.non_bad_ndrmle = non_bad_ndrmle
        #non negative courses but we don't care about the day, rm , lecturer and topic
        non_bad_ndrmletp = []
        for cor in list(onto.COURSE.instances()):
            if  cor not in self.bad_courses:
                non_bad_ndrmletp.append(cor)
        self.non_bad_ndrmletp = non_bad_ndrmletp
        return None
    """description: here the three schedules are created. Using the lists created before we create a schedule by searching for courses from the best list to the least optional, 
    until the schedule is complete(8 courses, 2 per period). We create backup courses for each period and use them to create the other schedules, by changing from the original schedule the courses that
    are fullfilling a smaller number of preferences. 
    At the creation of the schedules, we search if the course selected has a prerequisite and handle the situation by getting the prerequisite into the schedule.
    We use counters to be sure that the proper amount of courses is selected"""
    def schedules(self):
        schedules = []
        backup1 , backup2, backup3, backup4 = onto.CRS1, onto.CRS1, onto.CRS1, onto.CRS1
        schedule, p1, p2, p3,p4 = [], [], [], [], []
        c1,c2,c3,c4 = 2, 2, 2, 2
        for i in list(onto.MAN_COURSE.instances()):
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.courses_in_mind:
            if i.has_prereq:
                prereq = i.has_prereq
                for course in list(onto.COURSE.instances()):
                    if course.course_name == prereq:
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(course, c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4)
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(i, c1, c2, c3, c4, p1, p2, p3,p4, backup1,backup2,backup3,backup4)
        for i in self.best_courses:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                prereq = i.has_prereq
                for course in list(onto.COURSE.instances()):
                    if course.course_name == prereq:
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(course, c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4)
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.still_good_courses:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                prereq = i.has_prereq
                for course in list(onto.COURSE.instances()):
                    if course.course_name == prereq:
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(course, c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4)
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.still_good_courses_nf:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                prereq = i.has_prereq
                for course in list(onto.COURSE.instances()):
                    if course.course_name == prereq:
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(course, c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4)
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.still_good_courses_ne:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                prereq = i.has_prereq
                for course in list(onto.COURSE.instances()):
                    if course.course_name == prereq:
                        c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4 = self.check_period(course, c1, c2, c3, c4, p1, p2, p3, p4, backup1,backup2,backup3,backup4)
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.non_bad:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                continue
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.non_bad_nd:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                continue
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.non_bad_ndrm :
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                continue
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.non_bad_ndrmle:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                continue
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        for i in self.non_bad_ndrmletp:
            if c1 ==0 and c2 ==0 and c3 ==0 and c4 ==0:
                break
            if i.has_prereq:
                continue
            c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4 = self.check_period(i,c1,c2,c3,c4,p1,p2,p3,p4,backup1,backup2,backup3,backup4)
        if (c1 >0):
            for cour in list(onto.Period1C.instances()):
                if p1[0]!= cour:
                    p1.append(cour)
                    c1= c1-1
        if (c2 >0):
            for cour in list(onto.Period2C.instances()):
                if p2[0]!= cour:
                    p2.append(cour)
                    c2=c2-1
        if (c3 >0):
            for cour in list(onto.Period3C.instances()):
                if p3[0]!= cour:
                    p3.append(cour)
                    c3=c3-1
        if (c4 >0):
            for cour in list(onto.Period4C.instances()):
                if p4[0]!= cour:
                    p4.append(cour)
                    c4=c4-1
        if c1 < 1 and c2 < 1 and c3 < 1 and c4 < 1:
            schedule.append(p1)
            schedule.append(p2)
            schedule.append(p3)
            schedule.append(p4)
            schedules.append(schedule)
            for l in range(2):
                pa,pb,pc,pd = [], [], [] , []
                pa.append(p1[0])
                pb.append(p2[0])
                pc.append(p3[0])
                pd.append(p4[0])
                sc = []
                for i in range(4):
                    k = random.randint(0,2)
                    if k !=0:
                        if i ==0 and backup1 != onto.CRS1:
                            pa.append(backup1)
                        elif i ==1 and backup2 != onto.CRS1:
                            pb.append(backup2)
                        elif i ==2 and backup3 != onto.CRS1:
                            pc.append(backup3)
                        elif i==3 and backup4 != onto.CRS1:
                            pd.append(backup4)
                    elif k ==0:
                        if i ==0:
                            pa.append(p1[1])
                        elif i ==1:
                            pb.append(p2[1])
                        elif i ==2:
                            pc.append(p3[1])
                        elif i==3:
                            pd.append(p4[1])
                sc.append(pa)
                sc.append(pb)
                sc.append(pc)
                sc.append(pd)
                schedules.append(sc)
        return(schedules)
    """Inputs: the course, counters for each period, list of courses selected for each period, backup courses
     Output: all of the inputs except the course, they may be altered or not.
     Description: this function gets a course and the elements of the created schedule,
     then checks in what period it belongs, for that period he checks if it can be selected or two courses have already been selected,
     if it can not be selected and there is no backup course, this course becomes the backup for that period."""
    def check_period(self,cour,c1,c2,c3,c4,p1,p2,p3,p4,backup1, backup2, backup3, backup4):
        if cour in list(onto.Period1C.instances()):
            if c1>0:
                if cour not in p1:
                    p1.append(cour)
                    c1 = c1 - 1
            elif c1 == 0 :
                if cour not in p1:
                    backup1 = cour
                    c1 = c1 - 1
        elif cour in list(onto.Period2C.instances()):
            if c2>0:
                if cour not in p2:
                    p2.append(cour)
                    c2 = c2 - 1
            elif c2 == 0 :
                if cour not in p2:
                    backup2 = cour
                    c2 = c2 -1
        elif cour in list(onto.Period3C.instances()):
            if c3>0:
                if cour not in p3:
                    p3.append(cour)
                    c3 = c3 - 1
            elif c3 == 0 :
                if cour not in p3:
                    backup3 = cour
                    c3 = c3 -1
        elif cour in list(onto.Period4C.instances()):
            if c4>0:
                if cour not in p4:
                    p4.append(cour)
                    c4 = c4 - 1
            elif c4 == 0 :
                if cour not in p4:
                    backup4 = cour
                    c4 = c4 -1
        return(c1,c2,c3,c4,p1,p2,p3,p4,backup1, backup2,backup3,backup4)





if __name__ == "__main__":
    """Linking the ontology into the python script.
    IMPORTANT: for anyone to run the code, change the onto_path to the directory that has the ontology stored"""
    onto_path.append("C:/Users/nikos/Desktop/UnUtrecht/courses/IntelligentAgents/project/AgentCodes/finalVersion")
    onto = get_ontology("team9onto.owl").load()
    """Here follows a long list of questions and inputs from the user to gather his preferences"""
    name = input("Hello new student, please enter your name \n")
    assistance = True
    while assistance:
        exam = input("Do you prefer to have courses with final exams or not? TYPE 1 for YES or 2 for NO \n")
        if exam == "1":
            assistance = False
            exam = onto.EYES
        elif exam == "2":
            assistance = False
            exam = onto.ENO
    # FIND TOPIC PREFERENCES
    assistance = True
    while assistance:
        pref = input(
            "Do you have friends that already made a schedule?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            print(
                "Given the list of students, choose the numbers that you are friends with. TYPE the numbers and seperate each one with a space \n")
            st = list(onto.Student.instances())
            for i in range(len(st)):
                print(st[i].person_name)
                print("\n")
            fr = input("")
            nums = fr.split()
            friends = []
            for i in nums:
                k = int(i)
                friends.append(st[k])
                assistance = False
        elif pref == "2":
            friends = None
            break
    # FIND TOPIC PREFERENCES
    assistance = True
    while assistance:
        pref = input("Do you not prefer a specific topic and would like to avoid it?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            print(
                "Given the list of topics, choose the numbers you want to avoid. TYPE the numbers and seperate each one with a space \n")
            topics = input("1.AGENTS, 2.INTELLIGENT AGENTS, 3.MULTIAGENT SYSTEMS \n"
                           "4.COGNITIVE PROCESSING, 5.COGNITIVE MODELING, 6. COGNITIVE PSYCHOLOGY \n"
                           "7.LOGIC, 8. LOGIC AND COMPUTATION, 9. LOGIC AND PSYCOLOGY \n"
                           "10. MACHINE LEARNING\n")
            nums = topics.split()
            bd_topics = None
            bd_topics = []
            for i in nums:
                if int(i) == 1:
                    bd_topics.append(onto.AGENTS)
                    assistance = False
                elif int(i) == 2:
                    bd_topics.append(onto.INTELLIGENT_AGENTS)
                    assistance = False
                elif int(i) == 3:
                    bd_topics.append(onto.MULTIAGENT_SYSTEMS)
                    assistance = False
                elif int(i) == 4:
                    bd_topics.append(onto.COGNITIVE_PROCESSING)
                    assistance = False
                elif int(i) == 5:
                    bd_topics.append(onto.COGNITIVE_MODELING)
                    assistance = False
                elif int(i) == 6:
                    bd_topics.append(onto.COGNITIVE_PSYCHOLOGY)
                    assistance = False
                elif int(i) == 7:
                    bd_topics.append(onto.LOGIC)
                    assistance = False
                elif int(i) == 8:
                    bd_topics.append(onto.LOGIC_AND_COMPUTATION)
                    assistance = False
                elif int(i) == 9:
                    bd_topics.append(onto.LOGIC_AND_PSYCHOLOGY)
                    assistance = False
                elif int(i) == 10:
                    bd_topics.append(onto.MACHINE_LEARNING)
                    assistance = False
        elif pref == "2":
            bd_topics = None
            break
    # FIND RM PREFERENCES
    assistance = True
    while assistance:
        pref = input(
            "Do you not prefer a specific research methodology and would like to avoid it?  TYPE 1 for YES or 2 for NO \n")
        if pref == "1":
            print(
                "Given the list of RMs, choose the numbers you want to avoid. TYPE the numbers and seperate each one with a space \n")
            rms = input("1.CASE STUDY, 2.SIMULATION, 3.THEORY \n"
                        "4.SURVEY, 5.LITERATURE STUDY \n")
            nums = rms.split()
            bd_rms = []
            for i in nums:
                if int(i) == 1:
                    bd_rms.append(onto.RM1)
                    assistance = False
                elif int(i) == 2:
                    bd_rms.append(onto.RM2)
                    assistance = False
                elif int(i) == 3:
                    bd_rms.append(onto.RM3)
                    assistance = False
                elif int(i) == 4:
                    bd_rms.append(onto.RM4)
                    assistance = False
                elif int(i) == 5:
                    bd_rms.append(onto.RM5)
                    assistance = False
        elif pref == "2":
            bd_rms = None
            break
    # FIND LECTURER PREFERENCES
    assistance = True
    while assistance:
        pref = input(
            "Do you not prefer a specific lecturer and would like to avoid him/her?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            print(
                "Given the list of lecturers, choose the numbers you want to avoid. TYPE the numbers and seperate each one with a space \n")
            lects = input("1.PINAR, 2.ADAMS , 3.SIOPIS \n"
                          "4.MICHELS, 5.ERIKSEN, 6. BASHA \n"
                          "7.YOUNES, 8. BROWN, 9. ROSE \n"
                          "10.CUESTA\n")
            nums = lects.split()
            bd_lec = []
            for i in nums:
                if int(i) == 1:
                    bd_lec.append(onto.LEC1)
                    assistance = False
                elif int(i) == 2:
                    bd_lec.append(onto.LEC2)
                    assistance = False
                elif int(i) == 3:
                    bd_lec.append(onto.LEC3)
                    assistance = False
                elif int(i) == 4:
                    bd_lec.append(onto.LEC4)
                    assistance = False
                elif int(i) == 5:
                    bd_lec.append(onto.LEC5)
                    assistance = False
                elif int(i) == 6:
                    bd_lec.append(onto.LEC6)
                    assistance = False
                elif int(i) == 7:
                    bd_lec.append(onto.LEC7)
                    assistance = False
                elif int(i) == 8:
                    bd_lec.append(onto.LEC8)
                    assistance = False
                elif int(i) == 9:
                    bd_lec.append(onto.LEC9)
                    assistance = False
                elif int(i) == 10:
                    bd_lec.append(onto.LEC10)
                    assistance = False
        elif pref == "2":
            bd_lec = None
            break
    # FIND DAY PREFERENCE
    assistance = True
    while assistance:
        pref = input("Do you want to avoid a certain day of the week for the lecture?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            day = input("Type 1(Monday) through 5(FRIDAY). SELECT ONLY ONE DAY\n")
            if day == "1":
                day = onto.MO
                assistance = False
            elif day == "2":
                day = onto.TU
                assistance = False
            elif day == "3":
                day = onto.WE
                assistance = False
            elif day == "4":
                day = onto.TH
                assistance = False
            elif day == "5":
                day = onto.FR
                assistance = False
        elif pref == "2":
            day = None
            break
    # FIND UNPREFERRED COURSEs
    assistance = True
    while assistance:
        pref = input("Do you want to avoid a specific course ?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            print(
                "Given the list of courses, choose the numbers you want to avoid. TYPE the numbers and seperate each one with a space \n")
            crs = input("1.METHODS IN AI RESEARCH, 2.INTELLIGENT AGENTS, 3.INTRODUCTION TO MACHINE LEARNING \n"
                        "4.MUTLIAGENT SYSTEMS, 5.PHILOSOPHY OF AI, 6. DATA MINING \n"
                        "7.LOGIC AND LANGUAGE, 8. COMPUTATIONAL ARGUMENTATION, 9.DATA SCIENCE \n"
                        "10.COMPUTER VISION, 11.COGNITIVE MODELING, 12.PATTERN RECOGNITION \n"
                        "13.LOGIC AND COMPUTATION, 14.ALGORITHMS FOR DECISION SUPPORT, 15.PHILOSOPHY OF NEUROSCIENCE \n"
                        "16.TECHNOLOGIES FOR LEARNING, 17.SOCIAL COMPUTING, 18.NATURAL LANGUAGE PROCESSING \n"
                        "19.EXPERIMENTATION IN LINGUISTICS, 20.EVOLUTIONARY COMPUTING\n")
            nums = crs.split()
            bd_crs = []
            for i in nums:
                if int(i) == 1:
                    bd_crs.append(onto.CRS1)
                    assistance = False
                elif int(i) == 2:
                    bd_crs.append(onto.CRS2)
                    assistance = False
                elif int(i) == 3:
                    bd_crs.append(onto.CRS3)
                    assistance = False
                elif int(i) == 4:
                    bd_crs.append(onto.CRS4)
                    assistance = False
                elif int(i) == 5:
                    bd_crs.append(onto.CRS5)
                    assistance = False
                elif int(i) == 6:
                    bd_crs.append(onto.CRS6)
                    assistance = False
                elif int(i) == 7:
                    bd_crs.append(onto.CRS7)
                    assistance = False
                elif int(i) == 8:
                    bd_crs.append(onto.CRS8)
                    assistance = False
                elif int(i) == 9:
                    bd_crs.append(onto.CRS9)
                    assistance = False
                elif int(i) == 10:
                    bd_crs.append(onto.CRS1)
                    assistance = False
                elif int(i) == 12:
                    bd_crs.append(onto.CRS12)
                    assistance = False
                elif int(i) == 13:
                    bd_crs.append(onto.CRS13)
                    assistance = False
                elif int(i) == 14:
                    bd_crs.append(onto.CRS14)
                    assistance = False
                elif int(i) == 15:
                    bd_crs.append(onto.CRS15)
                    assistance = False
                elif int(i) == 16:
                    bd_crs.append(onto.CRS16)
                    assistance = False
                elif int(i) == 17:
                    bd_crs.append(onto.CRS17)
                    assistance = False
                elif int(i) == 18:
                    bd_crs.append(onto.CRS18)
                    assistance = False
                elif int(i) == 19:
                    bd_crs.append(onto.CRS19)
                    assistance = False
                elif int(i) == 20:
                    bd_crs.append(onto.CRS20)
                    assistance = False
                elif int(i) == 11:
                    bd_crs.append(onto.CRS11)
                    assistance = False
        elif pref == "2":
            bd_crs = None
            break
            # FIND COURSES IN MIND
    assistance = True
    while assistance:
        pref = input("Do you have a specific course in mind?  TYPE 1 for YES or 2 for NO \n")
        if pref == '1':
            print(
                "Given the list of courses, choose the numbers you have in mind. TYPE the numbers and seperate each one with a space \n")
            crs = input("1.METHODS IN AI RESEARCH, 2.INTELLIGENT AGENTS, 3.INTRODUCTION TO MACHINE LEARNING \n"
                        "4.MUTLIAGENT SYSTEMS, 5.PHILOSOPHY OF AI, 6. DATA MINING \n"
                        "7.LOGIC AND LANGUAGE, 8. COMPUTATIONAL ARGUMENTATION, 9.DATA SCIENCE \n"
                        "10.COMPUTER VISION, 11.COGNITIVE MODELING, 12.PATTERN RECOGNITION \n"
                        "13.LOGIC AND COMPUTATION, 14.ALGORITHMS FOR DECISION SUPPORT, 15.PHILOSOPHY OF NEUROSCIENCE \n"
                        "16.TECHNOLOGIES FOR LEARNING, 17.SOCIAL COMPUTING, 18.NATURAL LANGUAGE PROCESSING \n"
                        "19.EXPERIMENTATION IN LINGUISTICS, 20.EVOLUTIONARY COMPUTING\n")
            nums = crs.split()
            md_crs = []
            for i in nums:
                if int(i) == 1:
                    md_crs.append(onto.CRS1)
                    assistance = False
                elif int(i) == 2:
                    md_crs.append(onto.CRS2)
                    assistance = False
                elif int(i) == 3:
                    md_crs.append(onto.CRS3)
                    assistance = False
                elif int(i) == 4:
                    md_crs.append(onto.CRS4)
                    assistance = False
                elif int(i) == 5:
                    md_crs.append(onto.CRS5)
                    assistance = False
                elif int(i) == 6:
                    md_crs.append(onto.CRS6)
                    assistance = False
                elif int(i) == 7:
                    md_crs.append(onto.CRS7)
                    assistance = False
                elif int(i) == 8:
                    md_crs.append(onto.CRS8)
                    assistance = False
                elif int(i) == 9:
                    md_crs.append(onto.CRS9)
                    assistance = False
                elif int(i) == 10:
                    md_crs.append(onto.CRS1)
                    assistance = False
                elif int(i) == 12:
                    md_crs.append(onto.CRS12)
                    assistance = False
                elif int(i) == 13:
                    md_crs.append(onto.CRS13)
                    assistance = False
                elif int(i) == 14:
                    md_crs.append(onto.CRS14)
                    assistance = False
                elif int(i) == 15:
                    md_crs.append(onto.CRS15)
                    assistance = False
                elif int(i) == 16:
                    md_crs.append(onto.CRS16)
                    assistance = False
                elif int(i) == 17:
                    md_crs.append(onto.CRS17)
                    assistance = False
                elif int(i) == 18:
                    md_crs.append(onto.CRS18)
                    assistance = False
                elif int(i) == 19:
                    md_crs.append(onto.CRS19)
                    assistance = False
                elif int(i) == 20:
                    md_crs.append(onto.CRS20)
                    assistance = False
                elif int(i) == 11:
                    md_crs.append(onto.CRS11)
                    assistance = False
        elif pref == "2":
            md_crs = None
            break
    """Create the New student individual with all his relations filled"""
    student = onto.Student(name, namespace=onto, hasCoursesInMind=md_crs, isFriendWith=friends,
                           notPreferedLecturer=bd_lec, notPreferedRm=bd_rms,
                           notPreferedCourse=bd_crs, prefersExam=[exam],
                           notPreferedTopic=bd_topics ,notPrefferedDay=[day], person_name = [name])
    """run the reasoner after creating the student"""
    sync_reasoner(onto, infer_property_values=True)
    """construct our agent and run the only function needed to create the schedule"""
    my_agent = Agent(md_crs = md_crs , friends =friends , bd_lec =bd_lec, bd_rms=bd_rms, bd_crs=bd_crs, exam = exam , bd_topics= bd_topics ,day = day)
    my_agent.create_schedule()

