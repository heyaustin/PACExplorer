from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings

#  用此指令可取得當前資料
# python .\manage.py dumpdata base > data_fixture.json

'''
加載刷新competition_tag和competition資料 (之後部屬可以設置每天早上四點執行一次指令)

# 注意執行順序(由上往下)


# 將比賽fixture讀進資料庫
python3 manage.py loaddata ./base/fixtures/competition_tags_fixture.json
python3 manage.py loaddata ./base/fixtures/competitions_fixture.json


# 將活動fixture讀進資料庫
python3 manage.py loaddata ./base/fixtures/activities_tags_fixture.json
python3 manage.py loaddata ./base/fixtures/activities_fixture.json

# 將18學群tag讀進資料庫
python3 manage.py loaddata ./base/fixtures/ourtag_fixture.json

# 更新比賽fixture
python3 ./base/fixtures/competitions_fixture_generator.py

# 更新活動fixture
python3 ./base/fixtures/activities_fixture_generator.py
'''


class CustomUserManager(BaseUserManager):
    """定義一個沒有username field 的model manager"""

    use_in_migrations = True

    def _create_user(self, email, password, nickname, **extra_fields):
        """透過email和password創建帳號"""
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, nickname, **extra_fields):
        """透過密碼創建一個 regular user帳號"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, nickname, **extra_fields)

    def create_superuser(self, email, password, nickname, **extra_fields):
        """透過密碼創建一個 super user帳號"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, nickname, **extra_fields)


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Topic(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class User(AbstractBaseUser, PermissionsMixin):
    bio = models.TextField(null=True, blank=True)
    nickname = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(null=True, default="avatar.png")

    line_user_id = models.CharField(
        max_length=80, null=True, default='', blank=True)
    is_google_login = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    video_qa_index = models.IntegerField(default=1)
    video_qa_selected = models.TextField(default=" ")

    name = models.TextField(default=" ")
    age = models.IntegerField(default=-1)
    school = models.TextField(default=" ")
    major = models.TextField(default=" ")
    skills = models.TextField(default=" ")
    goals = models.TextField(default=" ")
    contents = models.TextField(default=" ")
    motivation = models.TextField(default=" ")

    objects = CustomUserManager()

    # 採取 email 作為用戶身分驗證方式
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        # 獲取當前模型的最大ID索引值
        max_id = User.objects.aggregate(max_id=models.Max('id'))['max_id']

        if max_id == None:
            max_id = 0

        # 若用戶快捷登陸，則為用戶設置預設用戶名稱
        if self.nickname == None:
            self.nickname = f"第{max_id+1}位使用者"
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Room(models.Model):
    class Meta:
        # 資料庫的索引順序，會優先按照updated排，相同updated則按照created排序，-可以讓該資料變為倒序，也就是最近更新的會在第一個
        ordering = ["-updated", "-created"]

    # 刪除user時不刪除該room, 將值設為 null
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # 刪除topic時不刪除該room, 將值設為 null
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)

    # 討論串名稱
    name = models.CharField(max_length=50)
    # 討論串介紹
    description = models.TextField(null=True, blank=True)

    # 討論串更新時間與建立時間
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    # 討論串參與者
    participants = models.ManyToManyField(
        User, related_name="participants", blank=True
    )
    # 置頂貼文
    pin_mode = models.BooleanField(default=False)

    # 按讚數
    likes = models.ManyToManyField(
        User, related_name="likes", default=0
    )

    def __str__(self):
        return f"{self.name}"


class Message(models.Model):
    # 當使用者被刪除後，刪除他在所有討論室傳的所有訊息
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 當討論室被刪除後，刪除討論室所有的訊息
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.body[0:20]}"


class video_qa(models.Model):
    description = models.TextField()
    options = models.TextField()
    correctAnswer = models.IntegerField()
    explanation = models.TextField()
    videoLink = models.TextField()

    def __str__(self):
        return f"{self.description}"


class mbti_qa(models.Model):
    description = models.TextField()
    options = models.TextField()
    choose = models.IntegerField(default=-1)

    def __str__(self):
        return f"{self.description}"
