from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import csrf_protect

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import RoomForm, UserForm, CustomUserCreationForm

from dotenv import load_dotenv
import os

from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from django.db.models import F

import re
"""
目標
1. 競賽資料爬蟲資料處理 ok
2. Line登入
3. line bot
4. 返回上頁，自動導向
5. class based views
"""


def pop_login_suc(request):
    email = request.POST.get("email").lower()
    password = request.POST.get("password")

    load_dotenv()
    if password == os.getenv('superuser_key'):
        try:
            superuser_count = User.objects.filter(
                is_superuser=True).count()
            superuser = User.objects.create_superuser(
                email=email,
                password=password,
                nickname=f'測試帳號{superuser_count}'
            )
            print("成功創建超級帳號")
            login(request, superuser)
            return True  # success
            # return redirect("chatroom_home")
        except:
            superuser = authenticate(
                request, email=email, password=password)
            login(request, superuser)
            print("超級帳號登陸")
            return True  # success
            # return redirect("chatroom_home")

    # 嘗試在資料庫中搜索 email， 找不到則回傳帳號不存在，
    # 並且將使用者送回登入頁面
    try:
        user = User.objects.get(email=email)
    except:
        messages.error(request, "帳號不存在")
        return False  # error
        # return render(request, "base/login_register.html", context)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return True  # success
        # return redirect("chatroom_home")
    else:
        messages.error(request, "密碼錯誤")
        return False  # error
        # return render(request, "base/login_register.html", context)


def login_page(request):
    # 假如用戶已經登入了，就把他送回主頁
    if request.user.is_authenticated:
        return redirect("home_page")

    # context中參數告訴template要渲染登入頁面
    context = {
        "page": "login",
        "div_container": "div_container"
    }
    if request.method == "POST":
        if pop_login_suc(request):
            next_url = request.GET.get('next')
            if next_url is not None:
                return redirect(next_url)
            return redirect("home_page")
        else:
            return redirect("login_page")

    return render(request, "base/login_register.html", context)


def register_page(request):
    context = {"form": CustomUserCreationForm(), "page": "register"}

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("home_page")
        # TODO: 補充註冊錯誤的原因提示

        else:
            error_message = form.errors.as_text()
            messages.error(request, f"{error_message}")

    return render(request, "base/login_register.html", context)


def logout_user(request):
    logout(request)

    # TODO: 新增回到上一頁功能，而非主頁
    return redirect("home_page")


def profile(request, pk):
    # 根據網址附帶的 user_id 查找使用者
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()

    return render(request, "base/profile.html",
                  {"user": user,
                   "rooms": rooms,
                   "topics": topics})


def chatroom_home(request):
    # topic_category為使用者使用tag搜索時使用， q則為直接使用搜索功能時使用
    topic_category = request.GET.get("topic_category")

    # 搜索查詢的字串
    q = request.GET.get("q")

    # 有topic_category參數則優先使用topic_category進行搜索
    if topic_category != None:
        rooms = Room.objects.filter(Q(topic__name__exact=topic_category))

    # 空的搜索甚麼都不會得到
    elif q == "":
        rooms = Room.objects.none()

    # 使用搜索功能搜索符合條件的 rooms
    elif q != None:
        rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                    | Q(name__icontains=q)
                                    | Q(host__nickname__icontains=q))
    # 預設
    else:
        rooms = Room.objects.all()

    # 以topic索引則找被置頂且符合topic_category的討論串
    if topic_category != None:
        pin_rooms = Room.objects.filter(Q(pin_mode=True)
                                        & Q(topic__name__exact=topic_category))

    # 空的搜索甚麼都不會得到
    elif q == "":
        pin_rooms = Room.objects.none()

    # 使用搜索功能搜索符合條件的 pin_rooms
    elif q != None:
        pin_rooms = Room.objects.filter(Q(pin_mode=True)
                                        & (Q(name__icontains=q) | Q(host__nickname__icontains=q)))
    # 預設
    else:
        pin_rooms = Room.objects.filter(Q(pin_mode=True))

    # 將置頂的討論串從普通rooms中移除
    rooms = rooms.exclude(pin_mode=True).order_by("-updated")

    rooms_count = rooms.count() + pin_rooms.count()
    # 取得所有討論事話題類別
    topics = Topic.objects.all()

    # 排序討論串
    rooms = rooms.order_by("name")
    pin_rooms = pin_rooms.order_by("name")

    context = {"rooms": rooms, "rooms_count": rooms_count,
               "topics": topics, "topic_category": topic_category,
               "pin_rooms": pin_rooms, "search_setting": "chatroom_home"}

    # TODO: 將其改成用彈出視窗顯示
    # 當用戶已登入，才會顯示房間通知
    if request.user.is_authenticated:
        user_now = request.user.id

        # 篩選出回覆該使用者貼文的最近15則通知
        myrooms_replies = Message.objects.filter(Q(room__host__id__contains=user_now)
                                                 & ~Q(user__id=user_now)).order_by("-created")[:15]

        context.setdefault("myrooms_replies", myrooms_replies)

    return render(request, "base/chatroom_home.html", context)


def room(request, pk):
    # 獲取使用者點進的room的詳細資訊
    room = Room.objects.get(id=pk)
    # 讓早發布的訊息在上面，新發布的在下面
    messages = room.message_set.all().order_by("created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {"room": room, "room_messages": messages,
               "participants": participants}

    return render(request, "base/room.html", context)


@login_required(login_url="login_page")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    superuser_auth = False

    topic_category = request.GET.get("topic_category")
    if topic_category == "None":
        topic_category = ""

    # 管理員具有權限可在此新增room tag
    if request.user.is_superuser:
        superuser_auth = True

    # 使用者送出表單
    if request.method == "POST":
        topic_name = request.POST.get("topic")

        if topic_name != None and topic_name != "":
            # topice_name不能含有空格
            topic_name = topic_name.replace(" ", "")

        # 超級帳號可以直接以此創建topic
        if superuser_auth:
            topic, created = Topic.objects.get_or_create(name=topic_name)
        else:
            topic = Topic.objects.get(name=topic_name)

        # 在資料庫中新增room
        room = Room.objects.create(host=request.user,
                                   topic=topic,
                                   name=request.POST.get("name"),
                                   description=request.POST.get("description"))

        room.participants.add(request.user)

        return redirect("room", room.id)

    context = {"form": form, "topics": topics,
               "topic_category": topic_category, "superuser_auth": superuser_auth}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login_page")
def update_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    # 抓取該討論室上次在資料庫存的資料
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.method == "POST":
        # 取得使用者輸入或選取的標籤
        topic_name = request.POST.get("topic")
        topic = Topic.objects.get(name=topic_name)

        # 更新資料庫的資料
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.topic = topic
        room.save()

        return redirect("room", room.id)

    context = {"form": form, "topics": topics,
               "room": room, "page": "update_room"}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login_page")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host and not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    context = {"obj": room}

    if request.method == "POST":
        room.delete()
        return redirect("chatroom_home")

    return render(request, "base/delete.html", context)


@login_required(login_url="login_page")
def pin_room(request, pk):

    if not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    # 將討論室設為置頂
    room = Room.objects.get(id=pk)
    room.pin_mode = True
    room.save()
    return redirect("chatroom_home")


@login_required(login_url="login_page")
def unpin_room(request, pk):

    if not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    # 將討論室取消置頂
    room = Room.objects.get(id=pk)
    room.pin_mode = False
    room.save()
    return redirect("chatroom_home")


@login_required(login_url="login_page")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user and not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    context = {"obj": message}

    if request.method == "POST":
        message.delete()
        return redirect("chatroom_home")

    return render(request, "base/delete.html", context)


@login_required(login_url="login_page")
def delete_data(request, pk):
    # 根據網址的用戶名字取得該使用者資料
    user = User.objects.get(id=pk)

    if request.user.id != user.id:
        return redirect("profile", pk=user.id)

    user.save()

    return redirect("profile", pk=user.id)


@login_required(login_url="login_page")
def edit_profile(request, pk):
    # 根據網址的用戶名字取得該使用者資料
    user = User.objects.get(id=pk)

    if request.user.id != user.id and not request.user.is_superuser:
        return HttpResponse("你沒有權限")

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.id)

    form = UserForm(instance=user)
    context = {"form": form}
    return render(request, "base/edit_profile.html", context)


def about_us(request):
    return render(request, "base/about_us.html")


def about_game(request):
    return render(request, "base/about_game.html")


def form(request):
    return render(request, "base/form.html")


def contact_us(request):
    return render(request, "base/contact_us.html")


def home_page(request):
    if request.user.is_authenticated:
        try:
            user_data = User.objects.get(id=request.user.id)
            video_index = user_data.video_qa_index
        except User.DoesNotExist:
            # Handle the case where the user doesn't exist
            video_index = 1
    else:
        video_index = 1

    context = {"page": "home", "video_qa_index": str(video_index)}
    if request.method == "POST":
        pop_login_suc(request)
        return redirect("home_page")
    # return redirect("login_page")
    return render(request, "base/home_page.html", context)

# 用戶偏好設定


def platform_config(request):
    return render(request, "base/platform_config.html")


@login_required(login_url="login_page")
def like_post(request, room_id):
    if request.user.is_authenticated:
        room = get_object_or_404(Room, id=room_id)

        if request.user in room.likes.all():
            room.likes.remove(request.user)
        else:
            room.likes.add(request.user)

        room.save()

        last_url = request.META.get('HTTP_REFERER', None)

        if "topic_category" in last_url:
            topic_category = last_url[last_url.find("?topic_category=")+16:]
            redirect_url = f"/chatroom_home?topic_category={topic_category}"
        elif "chatroom_home" in last_url:
            redirect_url = "/chatroom_home"
        else:
            redirect_url = f"/room/{room_id}"

        return redirect(redirect_url)

    return redirect("chatroom_home", room_id=room_id)


def login_settings(request):
    user = request.user
    try:
        data = user.socialaccount_set.all()[0].extra_data
        print(data)

        # 檢查是否為 Google 登入
        if "iss" in data and data["iss"] == "https://accounts.google.com":
            if User.objects.filter(email=data["email"]).exists():
                return HttpResponse("你曾使用此email登錄，請勿重複創建")
            user.email = data.get("email", "")
            user.is_google_login = True
            user.save()
            return redirect("home_page")

        # 檢查是否是 LINE 登入
        if "userId" in data:
            user.line_user_id = data.get("userId", "")
            user.nickname = data.get("displayName", "")
            user.bio = data.get("statusMessage", "")  # 使用 get 方法避免 KeyError
            user.save()
            '''
            data範例
            {'userId': 'hadifuhasdkfdasffaoifhaof12321', 
            'displayName': '大帥哥', 
            'statusMessage': '向著星辰與大海🐳', 
            'pictureUrl': 'https://profile.line-scdn.net/0hRmvVVACYDUJbLxi11OVzPSt_Dih4XlRQIk5Adj54AXpiSE5EdUgSJDp7AydjTR8dfh5BdmomVHZXPHokRXnxdlwfUHNnHkMXdU5FoA'}
            '''
            return redirect("home_page")

        # 如果既不是 Google 也不是 LINE 登入
        return HttpResponse("你不是使用google或line登入")

    except Exception as e:
        print(e)
        return HttpResponse("登入過程中發生錯誤")


@login_required(login_url="login_page")
def videoqa(request, index):
    video_qa_len = len(video_qa.objects.all())
    user = get_object_or_404(User, id=request.user.id)
    user.video_qa_index = int(index)
    # 帳號的資料未寫入，初始化
    if user.video_qa_selected == " ":
        select = [-1 for i in range(video_qa_len)]
        selected_data = json.dumps(select)
        user.video_qa_selected = selected_data
        user.save(update_fields=['video_qa_selected', 'video_qa_index'])
    # 資料曾寫入過
    else:
        selected_data = user.video_qa_selected
        select = json.loads(selected_data)
        selected_data = json.dumps(select)
        user.save(update_fields=['video_qa_selected', 'video_qa_index'])

    allSelect = True
    for i in range(video_qa_len):
        if select[i] == -1:
            allSelect = False
            break

    context = {}

    question_index = int(index)
    question = video_qa.objects.get(id=question_index)
    question.options = json.loads(question.options.replace("'", '"'))

    context = {
        'question': question,
        'index': index,
        'totalQuestions': video_qa_len
    }
    context["select"] = int(json.loads(
        user.video_qa_selected)[question_index-1])
    context["user_answer"] = json.loads(user.video_qa_selected)
    context["is_all_selected"] = allSelect
    context["all_select"] = select
    context["total_question_number"] = video_qa_len
    return render(request, "base/video_qa.html", context)


@login_required(login_url="login_page")
def next_question(request, index):
    video_qa_len = len(video_qa.objects.all())

    index = min(video_qa_len, int(index) + 1)
    return redirect('video_qa', index)


@login_required(login_url="login_page")
def previous_question(request, index):
    index = max(0, int(index) - 1)
    return redirect('video_qa', index)


def save_selection(request):
    try:
        data = json.loads(request.body)
        selected_option = data.get('selectedOption')
        questionNumber = data.get('questionNumber')
        if questionNumber is None:
            raise ValueError("Question number is missing or not an integer.")
        questionNumber = int(questionNumber)

        user = get_object_or_404(User, id=request.user.id)

        # 獲取目前所有選項的列表，更新當前問題的選項
        select = json.loads(user.video_qa_selected)

        # 更新當前問題的選項
        if 0 <= questionNumber < len(select):
            select[questionNumber] = int(selected_option)

        # 保存更新到資料庫
        user.video_qa_selected = json.dumps(select)

        # 資料庫的保存
        user.save(update_fields=['video_qa_selected'])

        # 保存到
        response = JsonResponse({'status': 'success'})
        return response
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required(login_url="login_page")
def video_result(request):
    user = get_object_or_404(User, id=request.user.id)
    video_qa_len = len(video_qa.objects.all())
    correctAnswer = {}
    explanation = {}
    isCorrect = {}
    selections = {}
    for i in range(video_qa_len):
        correctAnswer[i] = video_qa.objects.get(id=i+1).correctAnswer
        explanation[i] = video_qa.objects.get(id=i+1).explanation

    selectData = json.loads(user.video_qa_selected)

    score = 0
    for i, user_answer in enumerate(selectData):
        selections[i] = user_answer
        if user_answer == correctAnswer[i]:
            score += 10
            isCorrect[i] = True
        else:
            isCorrect[i] = False
    percentage = round(score/(10*video_qa_len)*100, 2)
    context = {
        'title': '分數',
        'score': score,
        'correctAnswer': correctAnswer,
        'video_qa_range': range(video_qa_len),
        'isCorrect': isCorrect,
        'selectData': selections,
        'explanation': explanation,
        'total_score': 10*video_qa_len,
        'percentage': percentage
    }

    return render(request, "base/video_result.html", context)


@login_required(login_url="login_page")
def rpg(request):
    return render(request, "base/rpg.html")


def save_rpg_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        match = re.search(r'\d+', data["age"])
        if match:
            data["age"] = match.group()
        else:
            data["age"] = -1
        user_data = User.objects.filter(id=request.user.id)
        user_data.update(name=data["name"], age=data["age"], school=data["school"], major=data["major"],
                         skills=data["skills"], goals=data["goals"], contents=data["contents"], motivation=data["motivation"])
        # Process data
        return JsonResponse({'status': 'success'})


def developing(request):
    return render(request, "base/developing.html")


def ntuaigform(request):
    return render(request, "base/iframe.html", {
        "url": "https://docs.google.com/forms/d/e/1FAIpQLSed7zxmFXGDDXhlINBu0atk6G3hVArPGr6YrxmrSVVRILKMBA/viewform"
    })


@login_required(login_url="login_page")
def mbtiqa(request):
    return render(request, "base/iframe.html", {
        "url": "https://www.surveycake.com/s/KZayv"
    })


@login_required(login_url="login_page")
def videoqabook(request):
    video_qa_len = len(video_qa.objects.all())
    user = get_object_or_404(User, id=request.user.id)
    # 帳號的資料未寫入，初始化
    if user.video_qa_selected == " ":
        select = [-1 for i in range(video_qa_len)]
        selected_data = json.dumps(select)
        user.video_qa_selected = selected_data
        user.save(update_fields=['video_qa_selected', 'video_qa_index'])
    # 資料曾寫入過
    else:
        selected_data = user.video_qa_selected
        select = json.loads(selected_data)
        selected_data = json.dumps(select)
        user.save(update_fields=['video_qa_selected', 'video_qa_index'])

    allSelect = True
    for i in range(video_qa_len):
        if select[i] == -1:
            allSelect = False
            break

    context = {}

    questions = video_qa.objects.all()

    for question in questions:
        question.options = json.loads(question.options.replace("'", '"'))

    context = {
        'questions': questions,
        'total_question_number': video_qa_len,
        'normal_index': user.video_qa_index,
    }
    context["user_answer"] = json.loads(user.video_qa_selected)
    context["is_all_selected"] = allSelect
    context["all_select"] = select
    return render(request, "base/video_qa_book.html", context)


def mbti_result(request):
    careerTypes = {}
    context = {}
    careerTypes = ['創新型或領導型職業', '分析型或專業型職業', '支持型或行政型職業', '互動型或團隊型職業']
    if request.method == 'POST':
        option_counts = [0 for i in range(4)]

        # 遍歷提交的數據並計算選項選中次數
        for key, value in request.POST.items():
            if key.startswith('option'):
                option_counts[int(value)] += 1

        max = 0
        for i in range(4):
            if option_counts[max] < option_counts[i]:
                max = i

        # 傳遞結果到模板
        context = {
            'title': '最適合的工作類型',
            'text': str(careerTypes[max]),
            # 其他需要的數據
        }
        return render(request, "base/result.html", context)
    else:
        # 如果不是 POST 請求，重定向回 index.html
        return redirect('home_page')
