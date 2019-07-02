import requests
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup
import urllib
import time

session = requests.session()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' + \
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
}

def get_captcha(r):
    image_name = 'captcha.png'
    with open(image_name, 'wb') as img:
        img.write(r.content)
        img.flush()
    img.close()

    image = Image.open(image_name)
    return image

def image_binarization_and_resize(image, threshold):
    image = image.convert('L')
    pixel_matrix = image.load()
    
    for column in range(0, image.height):
        for row in range(0, image.width):
            if pixel_matrix[row, column] > threshold:
                pixel_matrix[row, column] = 255
            else:
                pixel_matrix[row, column] = 0
    image = image.resize((1000, 500))
    return image

def regularization(result):
    exclude_list = ' .:\\|\'\"?[],()~@#$%^&*_+-={};<>/§'
    result = ''.join([ch for ch in result if ch not in exclude_list])
    result = result.replace('«', 'c').replace('¥', 'Y').replace('!', 'l')
    return result

def login(username, password):
    threshold = 127 # the value of the threshold based on the specific situation
    captcha_url = 'http://jwdep.dhu.edu.cn/dhu/servlet/com.collegesoft.eduadmin.tables.captcha.CaptchaController'
    
    # attampt for 10 times because of the low precision (approx. 50%)
    # of the captcha identification
    for i in range(10):
        try:
            response = session.get(url=captcha_url, headers=headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
        except:
            print('连接失败,请在校园网环境下或者使用VPN连接')
            exit()

        image = image_binarization_and_resize(get_captcha(response), threshold)
        result = regularization(pytesseract.image_to_string(image))
        
        information = {'userName': username, 'userPwd': password, 'code': result}
        hidden_url = 'http://jwdep.dhu.edu.cn/dhu/login_wz.jsp'
        try:
            connector = session.post(hidden_url, data=information, headers=headers, timeout=30)
            connector.raise_for_status()
            connector.encoding = connector.apparent_encoding
        except:
            print('网络连接失败,请重试')
            exit()
        if connector.text.find('同学你好') != -1:
            print('登录成功')
            return
            
    print('请检查帐号和密码,并重试')
    exit()

def get_name_and_score(course_id):
    url = 'http://jwdep.dhu.edu.cn/dhu/commonquery/selectcoursetermcourses.jsp?course=' + course_id
    try:
        download = session.get(url, headers=headers, timeout=100)
        download.raise_for_status()
        download.encoding = download.apparent_encoding
    except:
        print('网络中断,请保持网络畅通')
        exit()
    
    soup = BeautifulSoup(download.text, 'html.parser')
    name = urllib.request.quote(str(soup.a.string))
    score = str(soup.a.parent.next_sibling.next_sibling.next_sibling.next_sibling.string)
    return name, score

def validity_check(course_id, course_name, score):
    judge_url = r'http://jwdep.dhu.edu.cn/dhu/student/selectcourse/teachclasslist.jsp?courseId={}&courseName={}&score={}'.format(course_id, urllib.request.unquote(course_name), score)
    try:
        judge = session.get(judge_url, headers=headers, timeout=100)
        judge.raise_for_status()
        judge.encoding = judge.apparent_encoding
    except requests.exceptions.ConnectionError:
        print('课程有效性检测失败,请检查网络连接')
        exit()
    except requests.exceptions.HTTPError: # the webpage not exists, means the course is valid
        return True
    
    if judge.text.find('你这门课已经选了,不允许再次选择了') != -1:
        print('该课程已经选择')
    elif judge.text.find('该课程没有开放选课') != -1:
        print('该课程没有开放选课')
    elif judge.text.find('你这门课已经通过了') != -1:
        print('该课程已通过')
    return False

def course_selection(username, course_No, course_id):
    course_name, score = get_name_and_score(course_id)
    if not validity_check(course_id, course_name, score):
        return False
    
    selection_url = r'http://jwdep.dhu.edu.cn/dhu/student/selectcourse/selectcourse2.jsp?' \
          'courseNo={}&courseId={}&courseName={}'.format(course_No, course_id, course_name)
    try:
        selection = session.get(selection_url, headers=headers)
        selection.raise_for_status()
        selection.encoding = selection.apparent_encoding
    except:
        print('网络连接失败,请重试')
        exit()
        
    if selection.text.find('对不起人数已满') != -1:
        print('该课程人数已满, 请稍候再试')
        return False
    
    get_url = r'http://jwdep.dhu.edu.cn/dhu/student/selectcourse/selectcourse.jsp?' \
              'studentId={}&courseNo={}&courseId={}&yearTerm={}&selectCourseStatus={}'.format( \
                  username, course_No, course_id, '20192020a', '2')
    check_url = r'http://jwdep.dhu.edu.cn/dhu/servlet/com.collegesoft.eduadmin.tables.selectcourse.SelectCourseController'
    check_information = {'doWhat': 'selectcourse', 'courseId': course_id,
                         'courseNo': course_No, 'courseName': course_name,
                         'studentId': username, 'majorId': '111320',
                         'enterYear': '20'+username[:2]+'a', 'yearTerm': '20192020a',
                         'teacherId': '10103655++', 'selectCourseStatus': '2'}
    try:
        get = session.get(get_url, timeout=30, headers=headers)
        get.raise_for_status()
        get.encoding = get.apparent_encoding
        check = session.post(check_url, data=check_information, timeout=30, headers=headers)
        check.raise_for_status()
        check.encoding = check.apparent_encoding
    except:
        print('网络连接失败,请重试')
        exit()
    return selection_seccessful(course_id)

def selection_seccessful(course_id):
    url = r'http://jwdep.dhu.edu.cn/dhu/student/selectcourse/seeselectedcourse.jsp'
    
    r = session.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text.find(course_id) != -1

def main():
    username = '170910224' # str(input('学号:'))
    password = '430602199904254510' # str(input('密码:'))
    course_No = '231144	' # str(input('选课序号:'))
    course_id = '130132' # str(input('课程编号:'))

    login(username, password)
    while not course_selection(username, course_No, course_id):
        time.sleep(5)
    print('选课成功')
    
if __name__ == '__main__':
    main()
