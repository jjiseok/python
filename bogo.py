from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urljoin
from time import sleep
import sys
import re
import sqlite3
import time
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import threading
import requests
import webbrowser
from urllib.error import HTTPError
from PIL import Image, ImageTk, ImageFile

class Soup:
    def __init__(self):
        self.s = requests.Session()
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11", "Referer":None}

    def souping_get(self, url):
        self.s.headers.update(self.headers)
        d = self.s.get(url)
        c = d.text
        r = BeautifulSoup(c, 'html.parser')
        return r

    def souping_post(self, url, data, down_url_referer=None, bs=None, binary=None):
        if down_url_referer is None:
            self.s.headers.update(self.headers)
        else:
            h = {"Referer":down_url_referer}
            self.s.headers.update(self.headers)
            self.s.headers.update(h)
        d = self.s.post(url, data)
        if binary is True:
            c = d.text
        else:
            c = d.content

        if bs is None:
            r = BeautifulSoup(c, 'html.parser')
        else:
            r = c
        return r


class Win:
    def __init__(self, master):
        self.root = master
        self.soup = Soup()
        self.init_window()
        self.init_category()
        self.pre_url = "https://zipbogo.net/cdsb/board.php?board="
        self.post_url = "&category=&search=&keyword=&recom=&page="
        self.login_ok = False
        self.ing = False
        self.is_next_block = False
        self.category_selected = False
        self.root.bind('<Control-Key-x>', lambda e: root.destroy())
        self.entry_id.focus()
        self.all_child_window = {}        

    def init_window(self):
        # 메뉴
        self.menu_view_image_view = BooleanVar()
        self.menu_view_image_view.set(False)

        self.menubar = Menu(self.root) # 메뉴바

        self.filemenu = Menu(self.menubar, tearoff=0) # 파일 메뉴
        self.filemenu.add_command(label="종료", command=self.root.destroy)
        self.filemenu.add_separator() 

        self.menubar.add_cascade(label="파일", menu=self.filemenu) # 파일메뉴를 메뉴바에 등록

        self.viewmenu = Menu(self.menubar, tearoff=0) # 보기 메뉴
        self.viewmenu.add_checkbutton(label="이미지 보기", command=self.menu_command_image_view, variable=self.menu_view_image_view)
        self.menubar.add_cascade(label="보기", menu=self.viewmenu)

        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="프로그램 정보", command=self.menu_help_info)
        self.menubar.add_cascade(label="도움말", menu=self.helpmenu)

        self.root.config(menu=self.menubar) # 메뉴바를 메뉴에 등록        

        # 상단
        self.sp = Separator(self.root, orient=HORIZONTAL)
        self.sp.pack()

        self.frame = Frame(self.root)
        self.frame.pack(fill=X)

        self.label_category = Label(self.frame, text="목록")
        self.label_category.pack(side=LEFT)

        self.combo = Combobox(self.frame)
        self.combo.pack(side=LEFT)
        self.combo.bind("<<ComboboxSelected>>", lambda x: threading.Thread(target=self.combo_category_selection).start())
        self.combo.config(state='readonly')

        self.frame2 = Frame(self.frame)
        self.frame2.pack(side=RIGHT)

        self.label_category = Label(self.frame2, text="ID")
        self.label_category.pack(side=LEFT)

        self.entry_id = Entry(self.frame2, width=15)
        self.entry_id.pack(side=LEFT)
        self.entry_id.bind('<Return>', lambda x: threading.Thread(target=self.login).start())

        self.label_category = Label(self.frame2, text="PW")
        self.label_category.pack(side=LEFT)

        self.entry_pw = Entry(self.frame2, width=15, show="*")
        self.entry_pw.pack(side=LEFT)
        self.entry_pw.bind('<Return>', lambda x: threading.Thread(target=self.login).start())

        self.button_login = Button(self.frame2, text="로그인", command=lambda: threading.Thread(target=self.login).start())
        self.button_login.pack(side=LEFT)
        self.button_logout = Button(self.frame2, text="로그아웃", command=lambda: threading.Thread(target=self.logout).start())
        self.button_logout.pack(side=LEFT)

        self.frame3=Frame(self.root)
        self.frame3.pack(fill=X)

        self.label_category = Label(self.frame3, text="주소")
        self.label_category.pack(side=LEFT)

        self.sp = Separator(self.root, orient=HORIZONTAL)
        self.sp.pack()
        self.entry_address = Entry(self.frame3)
        self.entry_address.pack(fill=BOTH)
        self.button_logout.config(state=DISABLED)

        self.frame4=Frame(self.root)
        self.frame4.pack(fill=X)
        self.label_category = Label(self.frame4, text="아래 목록을 더블클릭하면 내용을 볼 수 있습니다.")
        self.label_category.pack(side=LEFT)
        # 트리뷰
        self.sp = Separator(self.root, orient=HORIZONTAL)
        self.sp.pack()
        self.frame_tree = Frame(self.root)
        self.frame_tree.pack(fill=BOTH, expand=1)
        self.tree = Treeview(self.frame_tree)
        self.tree_yscrollbar = Scrollbar(self.frame_tree, orient="vertical", command=self.tree.yview)
        self.tree_xscrollbar = Scrollbar(self.frame_tree, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=self.tree_yscrollbar.set, xscroll=self.tree_xscrollbar.set)
        self.tree["columns"] = ("no", "category", "title", "name", "date", "recommendation")
        self.tree.heading('#0', text="", anchor=W)
        self.tree.heading('#1', text="번호", anchor=W)
        self.tree.heading('#2', text="카테고리", anchor=W)
        self.tree.heading('#3', text="제목", anchor=W)
        self.tree.heading('#4', text="작성자", anchor=W)
        self.tree.heading('#5', text="날짜", anchor=W)
        self.tree.heading('#6', text="추천", anchor=W)
        self.tree.column("#0", width=0, stretch=0, minwidth=0)
        self.tree.column("#1", width=55, stretch=0, minwidth=0)
        self.tree.column("#2", width=90, stretch=0, minwidth=0)
        self.tree.column("#3", width=0, stretch=1, minwidth=0)
        self.tree.column("#4", width=80, stretch=0, minwidth=0)
        self.tree.column("#5", width=70, stretch=0, minwidth=0)
        self.tree.column("#6", width=50, stretch=0, minwidth=0)
        self.tree_xscrollbar.pack(side=BOTTOM, fill=X)
        self.tree_yscrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=1)
        self.tree.bind("<Double-1>", lambda x: threading.Thread(target=self.download_process).start())
        # 하단
        self.frame_b_base = Frame(self.root)
        self.frame_b_base.pack(fill=BOTH)
        self.frame_base = Frame(self.frame_b_base)
        self.frame_base.pack(side=RIGHT)
        self.combo_search = Combobox(self.frame_b_base, width=10)
        self.combo_search.pack(side=LEFT)
        self.entry_search = Entry(self.frame_b_base)
        self.entry_search.pack(side=LEFT)
        self.entry_search.bind('<Return>', lambda x: threading.Thread(target=self.button_search_start).start())
        self.button_search = Button(self.frame_b_base, text="검색", width=8, command=lambda: threading.Thread(target=self.button_search_start).start())
        self.button_search.pack(side=LEFT)
        self.button_page5 = Button(self.frame_base, text='첫5페이지', width=10, command=lambda: threading.Thread(target=self.button_view_page5).start())
        self.button_page5.pack(side=LEFT)
        self.combo_page = Combobox(self.frame_base, width=5, state="readonly")
        self.combo_page.bind("<<ComboboxSelected>>", lambda x: threading.Thread(target=self.combo_page_selection).start())
        self.combo_page.pack(side=LEFT)
        self.combo_page.config(state="readonly")
        self.Button_prev_page = Button(self.frame_base, text="◀", width=5, command=lambda: threading.Thread(target=self.button_prev_page).start())
        self.Button_prev_page.pack(side=LEFT)
        self.Button_next_page = Button(self.frame_base, text="▶", width=5, command=lambda: threading.Thread(target=self.button_next_page).start())
        self.Button_next_page.pack(side=LEFT)
        self.entry_page = Entry(self.frame_base, width=5)
        self.entry_page.pack(side=LEFT)
        self.entry_page.bind('<Return>', lambda x: threading.Thread(target=self.button_page_move).start())
        self.button = Button(self.frame_base, text="이동", width=5, command=lambda: threading.Thread(target=self.button_page_move).start())
        self.button.pack(side=LEFT)
        self.button_exit = Button(self.frame_base, text="종료", command=self.root.destroy)
        self.button_exit.pack(side=LEFT)
        self.progressbar = Progressbar(self.root, orient=HORIZONTAL, mode='determinate')
        self.progressbar.pack(fill=BOTH)
        self.combo_search['values'] = ("제목", "글쓴이", "내용")
        self.combo_search.config(state="readonly")
        self.combo_search.current(0)

    def init_category(self):
        self.category = {
        '01,newmovie':'영화-최신',
        '02,oldmovie':'영화-지난',
        '03,kormovie':'영화-한국',
        '04,hdmovie':'영화-DVD',
        '05,3dmovie':'영화-3D',
        '06,kdramaon':'한TV-방영드',
        '07,kdramaover':'한TV-종방드',
        '08,kentertain':'한TV-오락',
        '09,ksocial':'한TV-시사',
        '10,kcut':'한TV-분할',
        '11,fdramaon':'외TV-방영드',
        '12,fdramaover':'외TV-종방드',
        '13,fentertain':'외TV-오락/교양/다큐',
        '14,mmovie':'모바일-영화',
        '15,mktv':'모바일-한TV',
        '16,mftv':'모바일-외TV',
        '17,mani':'모바일-애니',
        '18,baby':'모바일-유아',
        '19,anion':'애니-방영',
        '20,aniover':'애니-종방',
        '21,kmp3':'MP3-국내',
        '22,fmp3':'MP3-해외',
        '23,filemusic':'뮤비',
        '24,torgame':'게임',
        '25,torbook':'만화,소설',
        '26,torutil':'유틸,강좌',
        '27,torandroid':'안드로이드',
        '28,toriphone':'아이폰',
        '29,torwindow':'윈도우',
        '30,smi':'자막나누기',
        '31,request':'요청'}
        t = ()
        for c, i in sorted(self.category.items()):
            t = t + (i, )
        self.combo['values'] = t

    def control_disabled(self, e):
        if e == "login_button":
            self.button_login.config(state=DISABLED)
        if e == "logout_button":
            self.button_logout.config(state=DISABLED)
        elif e == "text_id_pw":
            self.entry_id.config(state=DISABLED)
            self.entry_pw.config(state=DISABLED)

    def control_enabled(self, e):
        if e == "login_button":
            self.button_login.config(state=NORMAL)
        elif e == "logout_button":
            self.button_logout.config(state=NORMAL)
        elif e == "text_id_pw":
            self.entry_id.config(state=NORMAL)
            self.entry_pw.config(state=NORMAL)
        elif e == "login_button_text_id_pw":
            self.button_login.config(state=NORMAL)
            self.entry_id.config(state=NORMAL)
            self.entry_pw.config(state=NORMAL)

    def login(self):
        login_url = "https://zipbogo.net/cdsb/login_process.php"
        login_extern_url = "https://mybogo.net/cdsb/login_process_extern.php"
        login_id = self.entry_id.get()
        login_pw = self.entry_pw.get()
        if login_id != "" and login_pw != "":
            # 보고보고 로그인
            self.control_disabled("login_button")
            self.progressbar.config(mode="indeterminate")
            self.progressbar.start()
            html = self.soup.souping_post(login_url, {"mode":"login", "kinds":"outlogin", "user_id":login_id, "passwd":login_pw})
            if html.find("input", attrs={"name":"MEMBER_NAME"}) is not None:
                member_name = html.find("input", attrs={"name":"MEMBER_NAME"})['value']
                member_point = html.find("input", attrs={"name":"MEMBER_POINT"})['value']
                member_str = html.find("input", attrs={"name":"STR"})['value']
                member_todo = html.find("input", attrs={"name":"todo"})['value']
                data = {"MEMBER_NAME":member_name, "MEMBER_POINT":member_point, "STR":member_str, "todo":member_todo}
                # 마이보고 로그인
                html2 = self.soup.souping_post(login_extern_url, data)
                self.entry_id.delete(0, END)
                self.entry_pw.delete(0, END)
                self.entry_id.insert(END, unquote(unquote(member_name)))
                self.entry_pw.insert(END, member_point)
                self.login_ok = True
                self.control_enabled("logout_button")
                self.control_disabled("text_id_pw")
                self.entry_pw.config(show="")
                messagebox.showinfo("로그인 성공", re.compile('alert\("(.+?)"\)').search(html.decode('utf-8')).group(1))
            else:
                try:
                    messagebox.showerror("로그인 실패", re.compile('alert\("(.+?)"\)').search(html.decode('utf-8')).group(1))
                except:
                    messagebox.showerror("로그인 실패", "에러가 발생했습니다.")
                self.control_enabled("login_button")
            self.progressbar.stop()
            self.progressbar.config(mode="determinate")

    def logout(self):
        logout_url = "https://zipbogo.net/cdsb/login_process.php?mode=logout"
        logout_extern_url = "https://mybogo.net/cdsb/login_process_extern.php"
        self.progressbar.config(mode="indeterminate")
        self.progressbar.start()
        r = self.soup.souping_get(logout_url)
        r2 = self.soup.souping_post(logout_extern_url, {"todo":"logout_extern"})
        messagebox.showinfo("로그아웃", re.compile('alert\("(.+?)"\)').search(r.decode('utf-8')).group(1))
        self.logout_operation()
        self.progressbar.stop()
        self.progressbar.config(mode="determinate")

    def logout_operation(self):
        self.current_url = ""
        self.login_ok = False
        self.category_selected = False
        self.control_enabled("login_button_text_id_pw")
        self.control_disabled("logout_button")
        self.entry_id.delete(0, END)
        self.entry_pw.delete(0, END)
        self.entry_pw.config(show="*")

    def login_check(self):
        if self.login_ok is False:
            messagebox.showerror("에러", "로그인 중이 아닙니다.")
            return False

    def before_work(self):
        if self.ing == True:
            messagebox.showerror("에러", "처리중입니다.")
            return False

    def no_category_selected(self):
        if self.category_selected is False:
            messagebox.showerror("에러", "카테고리를 선택하지 않았습니다..")
            return False

    def combo_category_selection(self):
        if self.login_check() is False or self.before_work() is False:
            return
        combo_current = ""
        for key, value in self.category.items():
            if self.combo.get() == value:
                combo_current = key.split(",")[1]
        url = self.pre_url + combo_current + self.post_url + "1"
        self.main_process(url)
        self.category_selected = True

    # 첫 5페이지
    def button_view_page5(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        combo_current = ""
        for key, value in self.category.items():
            if self.combo.get() == value:
                combo_current = key.split(",")[1]
        c_url = self.pre_url + combo_current + self.post_url
        for i in range(1, 6):
            url = c_url + str(i)
            b = self.main_process(url, page5=True)
            if b == False:
                break
            time.sleep(0.1)

    def combo_page_selection(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        url = self.current_url.split("page=")[0] + "page=" + self.combo_page.get()
        self.main_process(url)

    def button_prev_page(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        page = int(self.current_url.split("page=")[1])
        if page == 1:
            messagebox.showinfo("에러", "페이지의 처음입니다.")
            return
        url = self.current_url.split("page=")[0] + "page=" + str(page - 1)
        self.main_process(url)

    def button_next_page(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        page = int(self.current_url.split("page=")[1])
        if self.is_next_block is False and self.combo_page['values'][len(self.combo_page['values']) - 1] == str(page):
            messagebox.showinfo("에러", "마지막 페이지입니다.")
            return
        url = self.current_url.split("page=")[0] + "page=" + str(page + 1)
        self.main_process(url)

    def button_page_move(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        s = self.entry_page.get()
        if s.isdigit() is False:
            messagebox.showinfo("에러", "숫자만 입력해 주세요.")
            return
        url = self.current_url.split("page=")[0] + "page=" + str(s)
        self.main_process(url)

    def progress(self, v):
        self.progressbar['value'] = v
        if v == 100:
            self.progressbar['value'] = 0
    # 검색
    def button_search_start(self):
        if self.login_check() is False or self.before_work() is False or self.no_category_selected() is False:
            return
        search_text = self.entry_search.get()
        search_condition = self.combo_search.get()
        if search_text == "":
            messagebox.showinfo("에러", "검색어를 입력하세요.")
            return
        s1 = self.current_url.split("&search=")[0] + "&search="

        if search_condition == "글쓴이":
            s_condition = "user_name"
        elif search_condition == "내용":
            s_condition = "contents"
        else:
            s_condition = "subject"

        s_condition = s_condition + "&keyword="
        s2 = "&recom=&page=1"
        url = s1 + s_condition + search_text + s2
        self.main_process(url)

    def main_process(self, url, page5=False):
        self.progressbar.config(mode="indeterminate")
        self.progressbar.start()
        b_result = False
        self.ing = True
        html = self.soup.souping_get(url)

        if html.find("td", align="center", colspan="6", style="width:50px") and html.find("td", style="width:50px").get_text(strip=True) == "등록된 글이 없습니다.":
            messagebox.showinfo("에러", "등록된 글이 없습니다.")

        elif html.find("tbody", class_="num") is not None:
            self.current_url = url
            self.entry_address.delete(0, END)
            self.entry_address.insert(END, url)
            # 목록 전체 삭제 여부
            if page5 is True and url[-1] == '1':
                self.tree.delete(*self.tree.get_children())
            elif page5:
                pass
            else:
                self.tree.delete(*self.tree.get_children())

            tr = html.find("tbody", class_="num").find_all("tr")
            ca = html.find("th", width="12%") # 카테고리가 없는 게시판
            for t in tr:
                if t.find("td").get_text(strip=True) == "[공지]":
                    continue
                if ca is None: # 카테고리가 없는 게시판
                    s_no = t.find("td").get_text(strip=True)
                    s_category = ""
                    s_title = t.find("td").find_next("td").get_text(strip=True).replace('\r\n', '')
                    if t.find("td").find_next("td").find("a") is None: # 블라인드 된 글 처리
                        continue
                    s_url = urljoin(self.current_url, t.find("td").find_next("td").find("a")["href"])
                    s_name = t.find("td").find_next("td").find_next("td").get_text(strip=True)
                    s_date = t.find("td").find_next("td").find_next("td").find_next("td").get_text(strip=True)
                    s_recommendation = t.find("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(strip=True)
                else: # 카테고리가 있는 게시판
                    s_no = t.find("td").get_text(strip=True)
                    s_category = t.find("td").find_next("td").get_text(strip=True)
                    s_title = t.find("td").find_next("td").find_next("td").get_text(strip=True).replace('\r\n', '')
                    if t.find("td").find_next("td").find_next("td").find("a") is None: # 블라인드 된 글 처리
                        continue
                    s_url = urljoin(self.current_url, t.find("td").find_next("td").find_next("td").find("a")["href"])
                    s_name = t.find("td").find_next("td").find_next("td").find_next("td").get_text(strip=True)
                    s_date = t.find("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(strip=True)
                    s_recommendation = t.find("td").find_next("td").find_next("td").find_next("td").find_next("td").find_next("td").get_text(strip=True)
                self.tree.insert("", END, s_url, values=(s_no, s_category, s_title, s_name, s_date, s_recommendation))

            #페이지 콤보 박스
            page_nums = html.find("td", bgcolor="#ebebeb", align="center").find_all(["a", "strong"])
            t_page = ()
            self.is_next_block = False
            for p in page_nums:
                if p.name == "strong":
                    s = p.get_text(strip=True)
                    self_current_page = s
                    t_page = t_page + (s, )
                elif p.name == "a" and p.get("class") is not None and p.get("class")[0] == "Font3":
                    s = p.get_text(strip=True)
                    t_page = t_page + (s, )
                elif p.find("img", src=True) is not None:
                    pt = p.find("img", src=True).get('src')[-9:]
                    if pt == "nexts.gif":
                        self.is_next_block = True
            self.combo_page['values'] = t_page
            b_result = True

        elif re.compile('alert\("(.+?)"\)').search(html.decode('utf-8')).group(1) == "잘못된 접근입니다.":
            messagebox.showerror("에러", re.compile('alert\("(.+?)"\)').search(html.decode('utf-8')).group(1))

        elif re.compile('alert\("(.+?)"\)').search(html.decode('utf-8')).group(1) == "게시판 접근 권한이 없습니다.":
            messagebox.showerror("에러", "로그인 중이 아닙니다.")
            self.logout_operation()
        else:
            messagebox.showerror("에러", "에러 발생")
        self.ing = False
        self.progressbar.stop()
        self.progressbar.config(mode="determinate")
        if b_result is False:
            return False

    def download_process(self):
        if self.login_check() is False or self.before_work() is False:
            return
        if self.tree.focus() == "":
            return

        self.ing = True
        self.progressbar.config(mode="indeterminate")
        self.progressbar.start()

        url = self.tree.focus()

        # url 중복 검사
        if url in self.all_child_window:
            messagebox.showwarning("오류 메시지", "해당 글이 이미 열려 있습니다.")
            self.progressbar.stop()
            self.progressbar.config(mode="determinate")
            self.ing = False
            return

        html = self.soup.souping_get(url)
        if html.find("tbody", class_="num") is not None:

            # 차일드 윈도우
            self.download_window_show(url, self.tree.item(url)['values'][2])
            current_top_window = self.all_child_window[url]
            current_top_window.download_url = url

            current_top_window.file_list = {}
            k = ()
            content = ""
            tr = html.find("tbody", class_="num").find_all("a", class_="link")
            for t in tr:
                if t.has_attr('val') is True:
                    val = t['val']
                    val2 = t['val2']
                    val3 = t['val3']
                    val4 = t['val4']
                    file_id = t['file_id']
                    title = t.get_text(strip=True)
                    current_top_window.file_list[title] = (val, val2, val3, val4, file_id)
                    
                else:
                    title = t['href']
                k = k + (title, )
            current_top_window.combo['values'] = k
            # 글의 내용
            content = html.find("tbody", class_="num").find("div", id="img_re")
            all_img = content.find_all("img")
            if all_img:
                    content = str(content).replace("<img", "[이미지]<img")
                    content = BeautifulSoup(content, "html.parser")
                    while content.find("img"):
                        content.img.unwrap()
            text_content = content.get_text("\n", strip=True)
            img_content = ""
            current_top_window.text.insert(END, text_content)
            all_img_url = []
            if all_img:
                current_top_window.text.insert(END, "\n\n\n" + "[이미지 목록]" + "\n")
                for img in all_img:
                    if img['src'][:6] == 'http://':
                        img_content = img['src'] + "\n"
                        current_top_window.text.insert(END, img_content, ('hyper', img_content))
                    elif img['src'].startswith('data:image'):
                        img_content = img['src'] + "\n"                        
                        current_top_window.text.insert(END, img['src'][:50] + "...\n", ('hyper', img_content))                        
                    else:
                        img_content = urljoin(url, img['src']) + '\n'
                        current_top_window.text.insert(END, img_content, ('hyper', img_content))
                    all_img_url.append(img_content[:-1])
            if all_img_url and self.menu_view_image_view.get():
                self.download_window_image_download(url, all_img_url) # 이미지 다운로드

        self.progressbar.stop()
        self.progressbar.config(mode="determinate")
        self.ing = False

    def menu_command_image_view(self):
        pass
    
    def webbrowser_open(self, t):
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'        
        webbrowser.get(chrome_path).open(t)

    def text_click(self, url):
        c = self.all_child_window[url].text.tag_names(CURRENT)

        if (c[0] == 'hyper'):
            self.webbrowser_open(c[1])            
        else:
            self.webbrowser_open(c[2])

    def download_window_scroll_frame(self, c):
        canvas = Canvas(c, borderwidth=0, height=105)
        frame = Frame(canvas)        
        hsb = Scrollbar(c, orient="horizontal", command=canvas.xview)        
        canvas.configure(xscrollcommand=hsb.set)
        
        canvas.pack(fill="both", expand=True)
        hsb.pack(fill="x")
        canvas.create_window((0,0), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

        return frame

        
    # 이미지 다운로드
    def download_window_image_download(self, o_url, all_img_url):
        j = 1
        c = self.all_child_window[o_url].download_bottom_frame
        a = self.download_window_scroll_frame(c)
        c.labels = {}
        for i in all_img_url:           

            url = i
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            try:
                u = urlopen(req)
            except HTTPError as e:                
                print(e.reason + ": ", url)
                continue
            
            file_name = "cached_images\\" + "file" + str(j)                      
            la = Label(a, text=str(j))
            la.pack(side=LEFT)
            
            la.bind("<Enter>", lambda x, l=la : l.config(cursor="hand2"))
            la.bind("<Leave>", lambda x, l=la : l.config(cursor=""))
            la.bind("<Button-1>", lambda e, url=i: self.webbrowser_open(url))            

            meta = u.info()
            
            if not meta.get("Content-Length"): # 이미지가 아니면 통과
                continue
            
            file_size = int(meta.get("Content-Length"))
            file_type = meta.get("Content-Type")
            if file_type == "image/jpeg":
                ext = ".jpg"
            elif file_type == "image/png":
                ext = ".png"
            elif file_type == "image/gif":
                ext = ".gif"
            else:
                ext = ""
            file_name = file_name + ext
            
            f = open(file_name, 'wb')
            file_size_dl = 0
            block_sz = 8192
            old_status=""
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                p = float(file_size_dl) / file_size
                status = "{0:.0%}".format(p)
                if status != old_status:
                    la["text"] = status
                old_status = status
                
            f.close()            
            
            image = Image.open(file_name)            
            resized = image.resize((100, 100),Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized)            
            la.config(image=photo)
            la.photo = photo
            image.close()
            
            j = j + 1

    def download_window_show(self, url, title):
        self.top = Toplevel()
        self.top.title(title)
        self.top.geometry('610x650+200+200')

        self.frame_top_address = Frame(self.top)
        self.frame_top_address.pack(fill=X)

        self.top_label = Label(self.frame_top_address, text=' 주소 ')
        self.top_label.pack(side=LEFT)

        self.top_entry = Entry(self.frame_top_address)
        self.top_entry.pack(side=LEFT, fill=X, expand=1)
        self.top_entry.insert(END, url)
        self.top_entry.config(state="readonly")

        self.frame_top_download = Frame(self.top)
        self.frame_top_download.pack(fill=X)

        self.frame_top_download2= Frame(self.frame_top_download)
        self.frame_top_download2.pack(side=LEFT)

        self.top_label = Label(self.frame_top_download2, text=' 다운로드 목록 ')
        self.top_label.pack()

        self.frame_top_download3= Frame(self.frame_top_download)
        self.frame_top_download3.pack(fill=X, side=LEFT, expand=True)

        self.top_combo = Combobox(self.frame_top_download3)
        self.top_combo.pack(fill=X)
        self.top_combo.config(state='readonly')

        self.frame_top_download4= Frame(self.frame_top_download)
        self.frame_top_download4.pack()
        #다운로드 버튼
        self.top_button = Button(self.frame_top_download4, text="다운로드", command=lambda: threading.Thread(target=self.link_open, args=(url,)).start())
        self.top_button.pack()
        #self.top.withdraw() # 창 숨기기
        #self.top.deiconify() # 창 보이기

        self.top_label = Label(self.top, text=' 본문내용')
        self.top_label.pack(fill=BOTH)

        self.frame_download_text = Frame(self.top)
        self.frame_download_text.pack(fill=BOTH, expand=1)
        self.top_text_scrollbar = Scrollbar(self.frame_download_text)
        self.top_text_scrollbar.pack(side=RIGHT, fill=Y)
        self.top_text = Text(self.frame_download_text)
        self.top_text.pack(fill=BOTH, expand=1)
        self.top_text.config(yscrollcommand=self.top_text_scrollbar.set)
        self.top_text_scrollbar.config(command=self.top_text.yview)

        # 다운로드 창에 이미지 보기
        self.download_bottom_sp1 = Separator(self.top, orient=HORIZONTAL)
        self.download_bottom_sp1.pack()
        self.download_bottom_frame = Frame(self.top)
        self.download_bottom_frame.pack(fill=X)        

        #self.download_bottom_label = Label(self.download_bottom_frame, text="이미지")
        #self.download_bottom_label.pack(side=LEFT)

        self.all_child_window[url] = self.top
        self.top.combo = self.top_combo
        self.top.button = self.top_button
        self.top.text = self.top_text
        self.top.download_bottom_frame = self.download_bottom_frame        

        self.top_text.tag_config("hyper", foreground="blue", underline=1)
        self.top_text.tag_bind("hyper", "<Enter>", lambda x: self.all_child_window[url].text.config(cursor="hand2"))
        self.top_text.tag_bind("hyper", "<Leave>", lambda x: self.all_child_window[url].text.config(cursor=""))
        self.top_text.tag_bind("hyper", "<Button-1>", lambda x: threading.Thread(target=self.text_click, args=(url,)).start())

        self.top.protocol("WM_DELETE_WINDOW", lambda: self.child_window_destroy(url))

    def child_window_destroy(self, url):

        if self.before_work() is False:
            return
        
        self.all_child_window[url].destroy()
        del self.all_child_window[url]

    def link_open(self, url):        
        current = self.all_child_window[url]

        s = current.combo.get()
        if s == "":
            messagebox.showerror("다운로드 오류", "파일이 선택되지 않았습니다.")
            current.deiconify()
            return

        if s.split(":")[0] == "magnet":
            current.text.insert(END, "\n\n" + s)
            current.text.see(END)
        else:            
            article_id = None
            for i in url.split("&"):
                if i.startswith("no=") == True:
                    article_id = i[3:]
            if not article_id:
                print("no article_id")
                return
            file_id = current.file_list[s][4]            
            down = current.file_list[s][0] # val
            filetype = current.file_list[s][3] # val4

            if filetype == "torrent":
                current.text.insert(END, "\n\n" + s + ".torrent - 다운로드 중...")
            else:
                current.text.insert(END, "\n\n" + s + " - 다운로드 중...")
            current.text.see(END)
            
            down_url = "https://zipbogo.net/cdsb/download.php"                        
            html = self.soup.souping_post(down_url, {"file_id" : file_id, "article_id" : article_id, "down" : down, "filetype" : filetype}, current.download_url)
            
            html = html.decode('utf-8').replace("\n", "").replace("{", "").replace("}", "")
            
            d_url = None
            valid_id = None
            code = None
            for i in html.split(","):
                if i.startswith('"key"'):
                    d_url = "http://linktender.net/" + i[7:-1]
                    code = i[7:-1]
                if i.startswith('"msg"'):
                    valid_id = i[7:-1]
            if not d_url or not valid_id or not code:
                print("no linktender url")
                return            
            
            vvvv = current.file_list[s][1]
            dddd = current.file_list[s][0]
            ssss = current.file_list[s][2]            
            
            html = self.soup.souping_post(d_url, {"vvvv" : vvvv, "dddd" : dddd, "ssss" : ssss, "code" : code, "file_id" : file_id, "valid_id" : valid_id}, current.download_url, binary=True)
            
            temp_html = html.find("form", id="myform")            
            
            if not temp_html:
                print("linktender no form")
                return

            dddd = temp_html.find("input", id="dddd")['value']
            vvvv = temp_html.find("input", id="vvvv")['value']
            file_id = temp_html.find("input", id="file_id")['value']
            valid_id = temp_html.find("input", id="valid_id")['value']          
            
            link_url = "http://linktender.net/execDownload.php"
            
            time.sleep(8)            
            html = self.soup.souping_post(link_url, {"vvvv" : vvvv, "dddd" : dddd, "file_id" : file_id, "valid_id" : valid_id}, d_url, bs = True)
            if filetype == "torrent":
                s = s + ".torrent"
            self.file_save(s, html)
            
            if url in self.all_child_window:
                current.text.insert(END, "\n\n" + s + " - 다운로드 완료")
                current.text.see(END)

    def file_save(self, s, html):
        f = open(s, "wb")
        f.write(html)
        f.close()

    def menu_help_info(self):
        messagebox.showinfo("프로그램 정보", "웹브라우저 v1.0")
        


if __name__ == "__main__":    
    root = Tk()
    Win = Win(root)
    root.title('웹브라우저')
    root.geometry('820x670+200+20')    
    root.mainloop() 
    
