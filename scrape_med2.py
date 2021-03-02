import requests
from bs4 import BeautifulSoup as bsp
from bs4 import Comment
from selenium import webdriver
import selenium.webdriver.support.ui as ui
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import pandas as pd
import os
import time
import tqdm
import sys
import lib
from urllib.request import urlopen
from urllib.parse import urlparse


driver = webdriver.Chrome("/home/min/chromedriver")
driver.maximize_window()
src = 'http://jmp.huemed-univ.edu.vn/'

def bs(driver):
    return bsp(driver.page_source, features='lxml')

def driver_get(driver, link, return_link=None):
    driver.get(link)
    while bs(driver).findAll('img', attrs={'src': '/registimage.aspx'}):
        print(link)
        input('Enter when finish verfifying.')
        if return_link:
            driver.get(return_link)
        else:
            driver.get(link)

def getting_hrefs():
    hrefs_source = []
    hrefs = []
    for i in range(1, 42):
        href = 'http://jmp.huemed-univ.edu.vn/ListBaibao.aspx?ffind=&Keyword=g7vn&Page={}'.format(i)
        hrefs_source.append(href)

    assert len(hrefs_source)==41
    print(hrefs_source[0])

    for source in hrefs_source:
        driver_get(driver, source)
        wait = ui.WebDriverWait(driver, 30)
        c = wait.until(lambda driver: 
                        bs(driver).findAll('a', attrs={"class": "linkheader"}))
        print(len(c))

        if not c:
            continue
        for link in c:
            href = link.get('href')
            href = src + href 
            hrefs.append(href)

    print(len(hrefs))
    assert len(hrefs)==1271

    count = 0
    new_hrefs = []

    for href in hrefs:
        if 'WebContent.aspx?id=128' in href:
            count += 1
        else:
            new_hrefs.append(href)

    assert count==41
    assert len(new_hrefs)==1230

    print(count)
    input()

    with open('tapchi_yduoc_hrefs.txt', 'w') as f:
        for href in new_hrefs:
            f.write(str(href) + '\n')

def get_text():
    with open('tapchi_yduoc_hrefs.txt', 'r') as f:
        hrefs = f.readlines()
    assert len(hrefs)==1230

    to_check = [] #len(en_sents)!=len(vi_sents))
    not_found = {} # href error
    # count = 0
    # redo_list = [364, 367, 368, 369, 375, 377, 379, 381, 384, 404, 407,
    #             410, 418, 419, 422, 460, 466, 467, 469, 471, 473, 474, 
    #             475, 476, 507, 637, 643, 664, 676, 701, 953, 956, 959, 
    #             964, 965, 966, 967, 968, 969, 971, 972, 973, 974, 975, 
    #             976, 977, 978, 979, 980, 983, 984, 985, 986, 987, 988, 
    #             989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 1000, 
    #             1001, 1002, 1003, 1004, 1005, 1006, 1007, 1009, 1010,
    #             1012, 1013, 1014, 1015, 1029, 1228]
    # print('num of redo: ', len(redo_list))
    # for i, href in enumerate(hrefs):
    # for i in tqdm.tqdm(range(len(hrefs))):
    for i in tqdm.tqdm(range(1230)):
        if not os.path.exists('med{}-tapchiyhoc.txt'.format(i)):
            # if i not in redo_list:
            print('round: ', i)
            href = hrefs[i]
            driver_get(driver, href)

            wait = ui.WebDriverWait(driver, 5)

            soup = bsp(driver.page_source, 'lxml')
            table = soup.find_all('div', id='ctl00_ContentG7VN_Panel1')
            if not table:
                # print('table not found')
                not_found[i] = href
                continue
                

            table = soup.find_all('div', id='ctl00_ContentG7VN_Panel1')[0]

            trs = table.find_all('tr')

            if not trs:
                # print('text not found')
                not_found[i] = href
                continue

            extract_texts = []
            get_texts = []
            en_texts = []
            vi_texts = []

            try:
                for tr in trs:
                    for td in tr.find_all('td'):
                        extract_texts.append(td.text)
                # print(i, 'extract_texts: ', len(extract_texts))
                
                # del extract_texts[2:5]
                
                # for text in extract_texts: 
                #     if text.strip() not in ['', ' ', '.', ':', '...']:
                #         get_texts.append(text)
                # # print(i, 'get_texts: ', len(get_texts))
                
                # for j, text in enumerate(get_texts):
                #     length = len(get_texts)
                #     if j==0:
                #         vi_texts.append(text)
                #     elif j==1:
                #         en_texts.append(text)
                #     elif j > 1 and j <= length//2: 
                #         vi_texts.append(text)
                #     elif j > length//2:
                #         en_texts.append(text)

                
            except:
                continue
            
            with open('med{}-tapchiyhoc.txt'.format(i), 'w') as f:
                for text in extract_texts:
                    f.write(text + '\n')
            # if en_texts and vi_texts:
            #     count += 1
            #     if not len(en_texts)==len(vi_texts):
            #         to_check.append(i)

            #     with open ('med{}_en.txt'.format(i), 'w') as f:
            #         for text in en_texts:
            #             f.write(text+'\n')

            #     with open ('med{}_vi.txt'.format(i), 'w') as f:
            #         for text in vi_texts:
            #             f.write(text+'\n')
            
            # time.sleep(1)
                        
    print('===========')
    print('Done')
    # print('Downloaded: ',count)
    # print('to check: ', len(to_check), '\n', to_check)
    # print('===========')
    # print()
    # for key in not_found:
    #     print(key,':  ', value)
    print(len(not_found))
    print(not_found.keys())

get_text()
input()

count = 0
for i in tqdm.tqdm(range(1230)):
    if os.path.exists('med{}-tapchiyhoc.txt'.format(i)):
        count += 1
print(count)

# 1120 files exist, but 29 cant be used.

# # 110 not_found or no_contents:
# not_found = [259, 500, 501, 502, 503, 504, 505, 506, 508, 509, 
#              510, 511, 512, 513, 514, 525, 592, 596, 608, 626, 
#              627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 
#              658, 839, 911, 935, 936, 937, 938, 939, 940, 941, 
#              942, 943, 944, 945, 946, 947, 948, 949, 950, 981, 
#              1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 
#              1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 
#              1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 
#              1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 
#              1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 
#              1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 
#              1098, 1099, 1100, 1101, 1103, 1104, 1105, 1106, 
#              1108, 1109, 1110, 1111])

# # 29 no en, no vi or no contents 
#     [117, 118, 120, 121, 122, 123, 124, 125, 126, 
#      507, 921, 922, 923, 924, 925, 926, 927, 928,
#      929, 930, 931, 932, 933, 934, 951, 637, 920,
#     1146, 1205]

# # from 1230 hrefs found, (110 + 29 = 139) cant be used.

def check_different_length():
    to_check = [55, 63, 213, 241, 245, 315, 317, 390, 402, 421, 429, 440, 441, 451, 452, 465, 472, 484, 499, 550, 621, 638, 639, 640, 644, 645, 646, 648, 649, 650, 663, 665, 666, 667, 719, 801, 884, 903, 913, 915, 958, 962, 970, 1011, 1016, 1102, 1107, 1179, 1188, 1206, 1217, 1222, 1224]
    assert len(to_check) == 53
    failed = []
    for num in tqdm.tqdm(to_check):
        enf0 = os.path.join(work_dir, 'med{}_en.txt'.format(num))
        vif0 = os.path.join(work_dir, 'med{}_vi.txt'.format(num))
        en_sents = lib.read_nonempty(enf0)
        vi_sents = lib.read_nonempty(vif0)

        if len(en_sents) > len(vi_sents):
            print('len(en_sents) > len(vi_sents)')

            dif = len(en_sents) - len(vi_sents)
            newsen_sents = en_sents[0:-dif]
            
            with open(enf0, 'w') as f:
                for sent in newsen_sents:
                    f.write(sent + '\n')

        if len(en_sents) < len(vi_sents):
            print('len(en_sents) < len(vi_sents)')
            
            dif = len(vi_sents) - len(en_sents)
            newsvi_sents = vi_sents[0:-dif]

            with open(vif0, 'w') as f:
                for sent in newsvi_sents:
                    f.write(sent + '\n')

        en_sents = lib.read_nonempty(enf0)
        vi_sents = lib.read_nonempty(vif0)

        if len(en_sents)!=len(vi_sents):
            failed.append(num)
        else:
            print('done well on ', num)

    print('failed', failed)

# NO USE =====================================================================================
# crd = os.getcwd()
# work_dir = os.path.join(crd, 'medic_txt', 'tapchi_Y-duoc')
# files = os.listdir(work_dir)
# re_check = {}
# with open('tapchi_yduoc_hrefs.txt', 'r') as f:
#     hrefs = f.readlines()
#     assert len(hrefs)==1230

# for i in tqdm.tqdm(range(1230)):
#     enf = os.path.join(work_dir, 'med{}_en.txt'.format(i))
#     vif = os.path.join(work_dir, 'med{}_vi.txt'.format(i))
#     en_sents = []
#     vi_sents = []
#     if os.path.exists(enf) and os.path.exists(vif):
#         # enfix = lib.fix_and_split(enf)
#         # vifix = lib.fix_and_split(vif)
#         en_sents_i = lib.read_nonempty(enf)
#         vi_sents_i = lib.read_nonempty(vif)
#         for sent in en_sents_i:
#             if sent not in ['Abstract:', 'Abstract', ]:
#                 en_sents.append(sent)

#         for sent in vi_sents_i:
#             if sent not in ['Tóm tắt bằng tiếng Việt:']:
#                 vi_sents.append(sent)
        
#         if len(en_sents)!=len(vi_sents):
#             re_check[i] = hrefs[i]

#         else:
#             if len(en_sents_i)!=len(en_sents):
#                 with open(enf, 'w') as f:
#                     for sent in en_sents:
#                         f.write(sent + '\n')

#             if len(vi_sents_i)!=len(vi_sents):
#                 with open(vif, 'w') as f:
#                     for sent in en_sents:
#                         f.write(sent + '\n')

# for key, value in re_check.items():
#     print(key, ': ', value)

# WORKING HERE                    #
# no en, no vi or no contents 
# 117 118 120 121 122 123 124 125 126 
# 507, 921 922 923
# 924 925 926 927 928
# 929 930 931 932 933
# 934 951
# 637, 920
#1146, 1205

# have contents 
# 367
# 368 369 375 377 379
# 381 384 404 407 410
# 418 419 422 460 466
# 467 469 471 473 474
# 475 476 643 664
# 676 701  953 956 959
# 964 965 966 967 968
# 969 971 972 973 974
# 975 976 977 978 979
# 980 983 984 985 986
# 987 988 989 990 991
# 992 993 994 995 996
# 997 998 1000 1001 1002
# 1003 1004 1005 1006 1007
# 1009 1010 1012 1013 1014
# 1015 1029 1228 

# 117 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10349&Nam=&id=203
# # no vi 
# 118 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10350&Nam=&id=203
# # no vi 
# 120 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10351&Nam=&id=203
# # no vi 
# 121 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10352&Nam=&id=203
# # no vi 
# 122 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10353&Nam=&id=203
# # no vi 
# 123 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10355&Nam=&id=203
# # no vi 
# 124 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10354&Nam=&id=203
# # no vi 
# 125 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10356&Nam=&id=203
# # no vi 
# 126 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10357&Nam=&id=203
# # no vi 
# 364 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=DAC_DIEM_LAM_SANG_VA_CAN_LAM_SANG_CUA_BENH_NHI__NGO_DOC_CHI_DIEU_TRI_TAI_TRUNG_TAM_CHONG_DOC__BENH_VIEN_BACH_MAI-9787&Nam=&id=183
# # re do getting text 
# 367 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=DANH_GIA_MUC_DO_CHINH_XAC_CUA_MOT_SO_CONG_THUC__TINH_TIEU_HAO_NANG_LUONG_LUC_NGHI_O_BENH_NHAN__THONG_KHI_NHAN_TAO_XAM_NHAP-9784&Nam=&id=183
# # re do getting text 
# 368 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=DANH_GIA_TINH_TRANG_PHAN_VE_O_KHOA_CAP_CUU__BENH_VIEN_HUU_NGHI_DA_KHOA_NGHE_AN-9770&Nam=&id=183
# # re do getting text 
# 369 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=GIA_TRI_NONG_DO_PARAQUAT_HUYET_TUONG__TRONG_TIEN_LUONG_DO_NANG_VA_TU_VONG_O_BENH_NHAN__NGO_DOC_CAP_PARAQUAT-9791&Nam=&id=183
# # re do getting text 
# 375 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=MOT_SO_YEU_TO_TIEN_LUONG_MUC_DO_CHUYEN_DANG__CHAY_MAU_NAO_O_BENH_NHAN_NHOI_MAU_NAO_CAP__DIEU_TRI_THUOC_TIEU_HUYET_KHOI_ALTEPLASE_DUONG_TINH_MACH-9783&Nam=&id=183
# # re do getting text 
# 377 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_DAC_DIEM_LAM_SANG_CHAN_THUONG_SO_NAO_MUC__DO_VUA_VA_NANG_O_KHOA_CAP_CUU_BENH_VIEN_TRUNG_UONG_HUE-9794&Nam=&id=183
# # re do getting text 
# 379 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NHAN_MOT_TRUONG_HOP_NGUNG_TUAN_HOAN_DUOC_CAP__CUU_THANH_CONG_THEO_PHAC_DO_MOI_CUA_AHA_2015__TAI_BENH_VIEN_DAI_HOC_Y_HA_NOI-9789&Nam=&id=183
# # re do getting text 
# 381 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=SO_SANH_GIA_TRI_DU_DOAN_SU_CAN_THIET_PHAI_THONG_KHI__NHAN_TAO_CUA_BANG_DIEM_BAP-65_VA_CURB-_65_O_BENH_NHAN__DOT_CAP_BENH_PHOI_TAC_NGHEN_MAN_TINH-9782&Nam=&id=183
# # re do getting text 
# 384 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=UNG_DUNG_KET_QUA_CHUP_CONG_HUONG_TU_VA_CHUP_CAT_LOP_VI_TINH_TRONG_PHAU_THUAT_MAU_TU_DUOI_MANG_CUNG_MAN_TINH_TAI_BENH_VIEN_DA_KHOA_HOP_LUC_THANH_HOA-9769&Nam=&id=183
# # re do getting text 
# 404 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=BENH_NAO_DAI_THAO_DUONG_TRONG__DAI_THAO_DUONG_TYP_2-9810&Nam=&id=184
# # re do getting text 
# 407 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=DANH_GIA_KET_QUA_DIEU_TRI_VIEM_MUI_XOANG_MAN_TINH_CO_VIEM_XOANG_BUOM_BANG_PHAU_THUAT_NOI_SOI_CHUC_NANG_MUI_XOANG-9840&Nam=&id=184
# # re do getting text 
# 410 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=GIA_TRI_CUA_ST_CHENH_LEN_O_aVR_TREN_BENH_NHAN_HOI_CHUNG_VANH_CAP_CO_HEP_THAN_CHUNG___DONG_MACH_VANH_TRAI_VA_HOAC___BENH_MACH_VANH_BA_NHANH-9811&Nam=&id=184
# # re do getting text 
# 418 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_DIEU_TRI_NHIEM_KHUAN_NIEU_O_BENH_NHAN___TAC_NGHEN_DUONG_TIET_NIEU_TREN_DO_SOI-9795&Nam=&id=184
# # re do getting text 
# 419 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_KIEN_THUC__THAI_DO__THUC_HANH_CHAM_SOC_SUC_KHOE_SINH_SAN_O_NU_nbsp__VI_THANH_NIEN_TAI_HUYEN_A_LUOI__TINH_THUA_THIEN_HUE-9837&Nam=&id=184
# # re do getting text 
# 422 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=VAI_TRO__IMA_Ischemia_Modified_Albumin___PHOI_HOP_VOI__hs-TROPONIN_T__hs-TnT__HUYET_THANH_TRONG_CHAN_DOAN_HOI_CHUNG_VANH_CAP_KHONG_ST_CHENH_LEN-9812&Nam=&id=184
# # re do getting text 
# 460 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_tinh_hinh_dieu_tri_noi_tru_benh_ly_khoi_u_tai_Khoa_Tai_Mui_Hong__Benh_vien_Truong__Dai_hoc_Y_Duoc_Hue-9855&Nam=&id=185
# # re do getting text 
# 466 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dac_diem_mo_benh_hoc_o_benh_nhan_u_lympho_ac_tnh_Hodgkin_va_khong__Hodgkin-9853&Nam=&id=185
# # re do getting text 
# 467 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dap_ung_xo_hoa_gan_o_benh_nhan_viem_gan_B_man_hoat_dong_dieu_tri_bang__Entecavir-9846&Nam=&id=185
# # re do getting text 
# 469 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_moi_lien_quan_giua_nong_do_lipoprotein-associated_phospholipsae_A2_huyet__thanh_voi_be_day_lop_noi_trung_mac_dong_mach_canh_o_benh_nhan_nhoi_mau_nao-9847&Nam=&id=185
# # re do getting text 
# 471 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_tinh_hinh_nuoi_con_hoan_toan_bang_sua_me_trong_sau_thang_dau_tai_thanh__pho_Hoi_An-9850&Nam=&id=185
# # re do getting text 
# 473 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Phan_tich_hoat_dong_marketing_doi_voi_san_pham_nexium__esomeprazol__cua_Cong_ty__Duoc_pham_Astrazeneca-9851&Nam=&id=185
# # re do getting text 
# 474 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Stress_va_cac_yeu_to_lien_quan_o_sinh_vien_Khoa_Y_te_Cong_cong__Truong_Dai_hoc_Y_Duoc_Hue-9854&Nam=&id=185
# # re do getting text 
# 475 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ty_le_roi_loan_thai_duong_ham_va_moi_lien_quan_voi_sai_khop_can_o_sinh_vien_rang_ham_mat__Truong_Dai_hoc_Y_Duoc_Hue-9857&Nam=&id=185
# # re do getting text 
# 476 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Vai_tro_cua_FGF23_trong_roi_loan_khoang_xuong_tren_benh_nhan_benh_than_man-9845&Nam=&id=185
# # re do getting text 
# 507 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-20362&Nam=&id=1201
# #no vi
# 637 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=ASSESSMENT_OF_DYSLIPIDEMIA_IN_PRE-DIABETIC_PATIENTS_WITH_ACUTE_CEREBRAL_INFARCTION-0&Nam=&id=202
# #no vi
# 643 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Cap_nhat_chan_doan_va_dieu_tri_ung_thu_da_day_som_2015-9556&Nam=2014&id=169
# # re do getting text 
# 664 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Phat_hien_RSV_o_benh_nhi_duoi_5_tuoi_bang_ky_thuat_realtime_RT-PCR_va_ky_thuat_rt-pcr_truyen_thong-9557&Nam=2014&id=169
# # re do getting text 
# 676 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Khang_insulin_o_benh_nhan_suy_tim-9521&Nam=2014&id=168
# # re do getting text 
# 701 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_span_style__line-height__115___font-family_____span_style__font-size__10pt___UNG_DUNG_DOPPLER__TRONG_DANH_GIA_SUC_KHOE_THAI__span___span_-0&Nam=&id=168
# # re do getting text 
# 920 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10331&Nam=&id=201
# # no vi
# 921 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10333&Nam=&id=201
# #no vi
# 922 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10332&Nam=&id=201
# #no vi
# 923 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10334&Nam=&id=201
# #no vi
# 924 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10335&Nam=&id=201
# #no vi
# 925 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10336&Nam=&id=201
# #no vi
# 926 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10337&Nam=&id=201
# #no vi
# 927 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10338&Nam=&id=201
# #no vi
# 928 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10339&Nam=&id=201
# #no vi
# 929 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10345&Nam=&id=201
# #no vi
# 930 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10340&Nam=&id=201
# #no vi
# 931 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10342&Nam=&id=201
# #no vi
# 932 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10341&Nam=&id=201
# #no vi
# 933 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10343&Nam=&id=201
# #no vi
# 934 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-10344&Nam=&id=201
# #no vi
# 951 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Hemoglobin_and_thalassemia-9285&Nam=2013&id=153
# #no vi
# 953 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_cac_yeu_to_nguy_co_trong_benh_viem_tac_dong_mach_chi_duoi_man_tinh-9433&Nam=2012&id=163
# # re do getting text 
# 956 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=De_xuat_thang_diem_tam_soat_tien_dai_thao_duong_va_dai_thao_duong_type_2_cho_nguoi_viet_nam_co_nguy_co-9434&Nam=2012&id=163
# # re do getting text 
# 959 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dac_diem_lam_sang___can_lam_sang_va_vi_khuan_ai_khi_cua_viem_amidan_man_tai_Benh_vien_Trung_uong_hue_va_Benh_vien_Dai_hoc_Y_Duoc_Hue-9436&Nam=2012&id=163
# # re do getting text 
# 964 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_XAY_DUNG_PHAN_MEM_GIAI_PHAU_AO_3_CHIEU____PHUC_VU_CHO_GIANG_DAY_GIAI_PHAU_HOC-9438&Nam=2012&id=163
# # re do getting text 
# 965 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ty_le_hien_mac_va_do_lan_rong_cua_mon_rang_o_can_bo_cong_nhan_Cong_ty_Quan_ly_duong_sat_Binh_Tri_Thien_nam_2011-9435&Nam=2012&id=163
# # re do getting text 
# 966 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Xac_dinh_mot_so_thanh_phan_hoa_hoc_chu_yeu_cua_mot_so_loai_thuc_vat_co_kha_nang_khang_khuan_tai_Thua_Thien_Hue-9437&Nam=2012&id=163
# # re do getting text 
# 967 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Cap_nhat_chan_doan_va_dieu_tri_benh_viem_khop_dang_thap-9431&Nam=2012&id=162
# # re do getting text 
# 968 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_ket_qua_dieu_tri_soi_than_ton_du_sau_mo_soi_duong_tiet_nieu_tren-9421&Nam=2012&id=162
# # re do getting text 
# 969 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_ket_qua_som_trong_dieu_tri_thoat_vi_ben_bang_tam_luoi_nhan__tao_co_nut__Mesh-plug_-9420&Nam=2012&id=162
# # re do getting text 
# 971 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Gia_tri_du_bao_huyet_khoi_tieu_nhi_trai_bang_thang_diem_CHADS2__CHADS2-VAS__cac_thong_so_sieu_am_tim_thanh_nguc_o_benh_nhan_rung_nhi_khong_co_benh_van_tim-9419&Nam=2012&id=162
# # re do getting text 
# 972 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=He_phan_tan_ran_nano_cua_thuoc_kho_tan-9418&Nam=2012&id=162
# # re do getting text 
# 973 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Hieu_qua_tan_soi_dien_thuy_luc_trong_dieu_tri_soi_mat_mo_lai-9423&Nam=2012&id=162
# # re do getting text 
# 974 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_benh_nguyen_benh_vi_nam_o_da_cua_benh_nhan__kham_tai_Benh_vien_truong_dai_hoc_Y_Duoc_Hue-9426&Nam=2012&id=162
# # re do getting text 
# 975 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_can_nguyen_vi_khuan_hieu_khi_gay_nhiem_khuan_benh_vien_tai_Benh_vien_Trung_uong_Hue_tu_thang_5_2011_den_thang_5_2012-9427&Nam=2012&id=162
# # re do getting text 
# 976 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_chat_luong_song_o_benh_nhan_suy_than_man_giai_doan_cuoi-9417&Nam=2012&id=162
# # re do getting text 
# 977 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dac_diem_lam_sang_va_vi_khuan_ai_khi_cua_viem_tay_-_ap_xe_quanh_amidan_tai_benh_vien_Trung_Uong_Hue_va_Benh_Vien_Truong_Dai_hoc_Y_Duoc_Hue-9425&Nam=2012&id=162
# # re do getting text 
# 978 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dap_ung_lam_sang__sinh_hoa_va_virus_sau_12_thang_dieu_tri_tenofovir_tren_benh_nhan_viem_gan_B_man_tinh-9416&Nam=2012&id=162
# # re do getting text 
# 979 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_hieu_qua_dieu_tri_Atorvastatin_phoi_hop_Aspirin_chong_viem_o_benh_nhan_nhoi_mau_nao_cap-9422&Nam=2012&id=162
# # re do getting text 
# 980 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_mot_so_dac_diem_lam_sang_va_can_lam_sang_cua_tre_so_sinh_gia_thang_dieu_tri_tai_khoa_nhi_Benh_vien_Truong_Dai_hoc_Y_Duoc_Hue-9424&Nam=2012&id=162
# # re do getting text 
# 983 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ty_le_suy_dinh_duong_va_nhiem_giun_rat_cao_o_tre_12_-_36_thang_tuoi__nguoi_Van_Kieu_va_Pakoh_tai_huyen_Dakrong__tinh_Quang_Tri-9430&Nam=2012&id=162
# # re do getting text 
# 984 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Xet_nghiem_HPV_trong_du_phong_ung_thu_co_tu_cung-9415&Nam=2012&id=162
# # re do getting text 
# 985 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Cap_nhat_thuoc_dieu_tri_buon_non_va_non-9414&Nam=2012&id=161
# # re do getting text 
# 986 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_hieu_qua_dieu_tri_liet_day_VII_ngoai_bien_do_lanh_bang_dien_cuc_dan_ket_hop_bai_thuoc__Dai_tan_giao_thang_-9409&Nam=2012&id=161
# # re do getting text 
# 987 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Du_bao_nguy_co_dai_thao_duong_type_2_bang_thang_diem_FINDRISC_o_benh_nhan_tien_dai_thao_duong___45_tuoi-9402&Nam=2012&id=161
# # re do getting text 
# 988 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_benh_ly_ha_duong_mau_giai_doan_so_sinh_som_tai_Khoa_Nhi__Benh_vien_Truong_Dai_hoc_Y_Duoc_Hue-9411&Nam=2012&id=161
# # re do getting text 
# 989 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_benh_nguyen_benh_vi_nam_o_da_cua_benh_nhan_kham_tai_Benh_vien_Truong_Dai_hoc_Y_Duoc_hue-9410&Nam=2012&id=161
# # re do getting text 
# 990 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dac_diem_lam_sang_va_vi_khuan_ai_khi_cua_viem_amidan_cap_tai_Benh_vien_Trung_uong_Hue_va_Benh_vien_Truong_Dai_hoc_Y_Duoc_Hue-9403&Nam=2012&id=161
# # re do getting text 
# 991 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_dac_diem_lam_sang__can_lam_sang_cua_viem_tieu_phe_quan_cap_o_tre_em_tu_2_thang_den_2_tuoi-9401&Nam=2012&id=161
# # re do getting text 
# 992 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_giai_phap_chong_su_xam_thuc_cua_cac_loai_reu_tren_cac_cong_trinh_kien_truc_thuoc_quan_the_di_tich_co_do_Hue-9408&Nam=2012&id=161
# # re do getting text 
# 993 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_HBV_DNA_va_HBeAg_o_benh_nhan_xo_gan_do_virus_viem_gan_B-9404&Nam=2012&id=161
# # re do getting text 
# 994 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_ket_qua_dieu_tri_ung_thu_gan_nguyen_phat_bang_dao_gamma_than_tai_Benh_vien_Truong_Dai_hoc_Y_Duoc_Hue-9407&Nam=2012&id=161
# # re do getting text 
# 995 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_mot_so_dac_diem_lam_sang__can_lam_sang_va_ket_qua_dieu_tri_viem_mang_nao_do_Streptococcus_suis_tai_Benh_vien_Trung_uong_Hue_nam_2011-2012-9405&Nam=2012&id=161
# # re do getting text 
# 996 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_tham_dinh_hieu_luc_phuong_phap_lai_va_ung_dung_de_thu_nghiem_noi_doc_to_vi_khuan-9406&Nam=2012&id=161
# # re do getting text 
# 997 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Phan_tich_moi_lien_quan_nhan_qua_trong_cong_thuc_vien_nen_phong_thich_co_kiem_soat_bang_toa_do_song_song-9412&Nam=2012&id=161
# # re do getting text 
# 998 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Tang_sinh_kha_dung_cac_thuoc_kho_tan_bang_he_phan_tan_ran-9400&Nam=2012&id=161
# # re do getting text 
# 1000 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Tong_hop_va_khao_sat_hoat_tinh_uc_che_Acetylcholinesterase_in_silico_va_in_vitro_mot_so_dan_chat_chalcon-9413&Nam=2012&id=161
# # re do getting text 
# 1001 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Cap_nhat_ve_dieu_tri_dai_thao_duong_typ_2-9399&Nam=2012&id=160
# # re do getting text 
# 1002 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Chiet_xuat__phan_lap_va_xac_dinh_cau_truc_Madecassoid_tu_rau_ma__Centella_asiatica__L.__Urb.-Apiaceae_-9391&Nam=2012&id=160
# # re do getting text 
# 1003 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Danh_gia_ket_qua_phau_thuat_cat_thuc_quan_noi_soi_nguc_trong_dieu_tri_ung_thu_thuc_quan-9395&Nam=2012&id=160
# # re do getting text 
# 1004 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Dieu_tri_nang_ong_mat_chu_bang_phau_thuat_noi_soi-9392&Nam=2012&id=160
# # re do getting text 
# 1005 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Hai_hop_chat_Polyoxygenated_Steroid_phan_lap_tu_loai_san_ho_mem_Sinularia_Cruciata-9393&Nam=2012&id=160
# # re do getting text 
# 1006 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ket_qua_buoc_dau_nghien_cuu_nong_do_nano_bac_co_the_ung_dung_trong_cong_tac_chong_nhiem_khuan_benh_vien-9388&Nam=2012&id=160
# # re do getting text 
# 1007 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ket_qua_lau_dai_dieu_tri_ung_thu_da_day_bang_phau_thuat_cat_doan_da_day_va_vet_hach_chang_2__chang_3-9397&Nam=2012&id=160
# # re do getting text 
# 1009 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_cac_thong_so_anh_huong_den_qua_trinh_tham_dinh_hieu_luc_phuong_phap_tiet_khuan-9390&Nam=2012&id=160
# # re do getting text 
# 1010 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_kien_thuc__thai_do__thuc_hanh_phong_chong_nhiem_HIV_cua_nhom_nam_quan_he_tinh_duc_dong_gioi_tinh_Khanh_Hoa_nam_2010-9396&Nam=2012&id=160
# # re do getting text 
# 1012 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_mot_so_dac_diem_lam_sang_va_can_lam_sang_benh_ta_o_Ben_Tre_2010-9387&Nam=2012&id=160
# # re do getting text 
# 1013 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_tham_dinh_hieu_luc_quy_trinh_tiet_khuan_bang_nhiet_am-9394&Nam=2012&id=160
# # re do getting text 
# 1014 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_ung_dung_phau_thuat_dat_tam_nhan_tao_hoan_toan_ngoai_phuc_mac_qua_noi_soi_trong_dieu_tri_benh_ly_thoat_vi_ben-9385&Nam=2012&id=160
# # re do getting text 
# 1015 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_ung_dung_phuong_phap_de_khong_dau_bang_gay_te_ngoai_mang_cung-9389&Nam=2012&id=160
# # re do getting text 
# 1029 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_su_bien_doi_nong_do_CK__CK-MB_va_Troponin_T_trong_mau_o_tre_giai_doan_so_sinh_som_co_ngat-9368&Nam=2012&id=159
# # re do getting text 
# 1146 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Thong_tin_Y_Duoc_hoc-9318&Nam=2011&id=156
# #no content
# 1205 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Xac_dinh_da_hinh_C677T_tren_gene_MTHFR_bang_ky_thuat_PCR-RFLP_nbsp___div_-10104&Nam=&id=175
# #no content
# 1228 :  http://jmp.huemed-univ.edu.vn/View.aspx?idbb=TY_LE_HOI_CHUNG_CHUYEN_HOA_O_BENH_NHAN_SUY_THAN_MAN_DIEU_TRI_BAO_TON_TAI_BENH_VIEN_DA_KHOA_TRUNG_UONG_CAN_THO-9300&Nam=&id=155
# # re do getting text 
# ===============================
#     assert len(en_sents)==len(vi_sents)
# with open('tapchi_yduoc_en.txt', 'w') as f:
#     for sent in en_sents:
#         f.write(sent + '\n')

# with open('tapchi_yduoc_vi.txt', 'w') as f:
#     for sent in vi_sents:
#         f.write(sent + '\n')

    #     en_sent_i = lib.read_nonempty(enf)
    #     vi_sent_i = lib.read_nonempty(vif)
    # for sent in en_sent_i:
    #     sents = sent.split('.')

    #     for sent in sents:
    #         if sent not in ['Abstract:', 'Abstract', ]:
    #             en_sents.append(sent)
    
    # for sent in vi_sent_i:
    #     sents = sent.split('.')

    #     for sent in sents:
    #         if sent not in ['Tóm tắt bằng tiếng Việt:']:
    #             vi_sents.append(sent)
    # for j in range(len(en_sents)):
    #     print(en_sents[j])
    # for j in range(len(vi_sents)):
    #     print(vi_sents[j])
    # print('en: ', len(en_sents))
    # print('vi: ', len(vi_sents))
    
# print('Done all')


# =============================
# re_do = [213, 241, 421, 440, 441, 452, 472, 484, 499, 550, 621, 638, 639, 640, 644, 645, 646, 648, 649, 650, 663, 665, 666, 667, 719, 801, 884, 903, 913, 915, 958, 962, 970, 1011, 1016, 1102, 1107, 1179, 1188, 1206, 1217, 1224]t
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_do_on_dinh_cua_com_pha_hon_dich_chua_glucomannan_tu_cu_nua_amorphophallus_paeoniifolius__ho_ray___araceae__trong_tai_thua_Thien_Hue-10081&Nam=&id=194

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Tinh_trang_dinh_duong_cua_benh_nhan_dieu_tri_noi_tru_tai_Benh_vien_Truong_Dai_hoc_Y_Duoc_Hue__div_-10030&Nam=&id=192

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_SU_BIEN_DOI_NONG_DO_PROCALCITONIN_HUYET_THANH_O_BENH_NHAN_BENH_THAN_MAN_GIAI_DOAN_CUOI-9806&Nam=&id=184

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Tim_hieu_moi_lien_quan_giua_nong_do_ferritin_huyet_thanh_voi_tinh_trang_thua_can_beo_phi__bilan_lipid_va_chi_so_so_vua_tren_benh_nhan_tang_huyet_ap-9928&Nam=&id=190

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Ty_le__dac_diem_va_nguyen_nhan_tai_nan_thuong_tich_tre_em_tai_thanh_pho_Buon_Ma_Thuot__tinh_Dak_Lak-9930&Nam=&id=190

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_tien_luong_nhoi_mau_nao_cap_bang_thang_diem_Plan_tai_Benh_vien_Trung_uong_Hue_nbsp_-9933&Nam=&id=189

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nhan_mot_truong_hop_do_soi_tui_mat_vao_ta_trang_gay_tac_ruot_non_tai_benh_vien_da_khoa__Khanh_Hoa-9848&Nam=&id=185

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Kien_thuc__thai_do_va_thuc_hanh_phong_chong_viem_nhiem_sinh_duc_duoi_cua_phu_nu_Khmer_trong_do_tuoi_15-49_tai_Can_Tho_nam_2016-9665&Nam=2016&id=171

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Viem_da_day_man_do_helicobacter_pylori__hieu_qua_tiet_tru_cua_phac_do_bon_thuoc_co_BISMUTH__EBMT_-9670&Nam=2016&id=171

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Canh_bao_ve_tinh_trang_cac_tap_chi_khoa_hoc_thuoc__danh_sach_den_-9725&Nam=2015&id=174
# #no english
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Nghien_cuu_thuc_hanh_phong_chong_sot_xuat_huyet_va_cac_yeu_to_lien_quan_cua_sinh_vien_Dai_Hoc_Hue_nbsp___div_-10200&Nam=&id=178
# # no content
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=FROM_INTRAVENOUS_UROGRAPHY_TO_CT_-_INTRAVENOUS_UROGRAPHY-20332&Nam=&id=202
# #no vietnamese
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NERVES_INVOLVEMENT_IN_HERPES_ZOSTER-0&Nam=&id=202
# # no vietnamese
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=An_overview_of_sleep_apnea_syndrome-10306&Nam=&id=199
# # no vietnamese
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Clarithromycin_and_Levofloxacin_susceptibility_testing_for_Helicobacter_pylori_nbsp__in_Central_Vietnam__Comparison_of_nbsp__E-test_and_disk_diffusion_methods-10301&Nam=&id=199
# # no vietnamese
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Clinical_features_and_treatment_result_of_pharyngitis_at_Hue_University_Hospital-10307&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=CME___A_review_of_laboratory_diagnosis_of_tuberculosis-10312&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Effectiveness_of__swim-up__and__gradient__methods_in_sperm_preparation_for_artificial_insemination-10305&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Effects_of_MECAMIX_in_burns_treatment_and_its_acute_toxicity-10309&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Endoscopic_features_and_risk_factors_of_esophageal_variceal_bleeding_in_cirrhotic_patients-10311&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Overview__nbsp_Molecular_techniques_in_monitoring_minimal_residual_disease_in_leukemia-10300&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Role_of_endoscopy_ultrasound_in_the_diagnosis_of_pancreatico-biliary_diseases_at_Hue_University_Hospital-10302&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Study_of_serum_S100_and_NSE_concentration_in_patients_with_acute_cerebral_infarction_at_Intensive_Care_Unit_of_Hue_Central_Hospital-10303&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Survey_of_elastic_indexes_of_the_ascending_aorta_by_echocardiography_in_sportsperson_with_different_types_of_exercise-10310&Nam=&id=199
# # no vi
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Bo_tuc_kien_thuc_sau_dai_hoc__Cap_nhat_dieu_tri_suy_giap_nguoi_lon__ATA___AACE_2012_-9191&Nam=2014&id=149
# # no en 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Nghien_cuu_dac_diem_hinh_anh_sieu_am_va_cat_lop_vi_tinh_chan_thuong_than__div_-10181&Nam=&id=182
# # no en 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu__do_thanh_thai_ure_tuan__do_thanh_thai_creatinin_tuan_o_benh_nhan_suy_than_man_giai_doan_cuoi_tham_phan_phuc_mac-9470&Nam=2013&id=165

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Xac_dinh_ham_luong_polyphenol_toan_phan__kha_nang_triet_tieu_goc_tu_do__kha_nang_uc_che_men_alph-glucosidase_va_hieu_qua_kiem_soat_duong_huyet_tren_chuot_dai_thao_duong_cua_san_pham_VOS_chiet_tach_tu_la_voi__la_oi__la_sen-9467&Nam=2013&id=165

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_tac_dung_chong_Oxy_hoa_cua_cay_Xuan_hoa_Pseuderanthemum_radlk_tren_chuot_nhat_trang__swiss_-9450&Nam=2013&id=164

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Su_hinh_thanh__phat_trien_va_ket_qua_cua_ung_dung_dong_vi_phong_xa_va_Y_hoc__Y_hoc_hat_nhan__tai_Viet_Nam-9446&Nam=2013&id=164

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Khao_sat_nong_do_Homocystein__CRP_huyet_thanh_o_benh_nhan_dai_thao_duong_type_2_phat_hien_lan_dau_tai_thanh_pho_Da_Nang-9445&Nam=2012&id=163

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_nong_do_ferritin_huyet_thanh_o_benh_nhan_tai_bien_mach_mau_nao-9444&Nam=2012&id=163

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Gia_tri_cua_su_bieu_lo_Her2_bang_ky_thuat_hoa_mo_mien_dich_tren_mau_mo_ung_thu_da_day_sinh_thiet_qua_noi_soi-9428&Nam=2012&id=162

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_moi_lien_quan_giua_nong_do_CEA_va_cac_dac_diem_lam_sang__giai_phau_benh_trong_ung_thu_bieu_mo_dai_truc_trang-9398&Nam=2012&id=160

# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Thong_tin_Y_Duoc_hoc_br___-9734&Nam=&id=160
# # no content 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=20121516&Nam=2012&id=151
# # no vi 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=201215110&Nam=2012&id=151
# # no vi 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Nghien_cuu_ung_dung_dinh_chi_thai__lt__49_ngay_tuoi_bang_Mifepristone_va_Misoprostol_nbsp__nbsp___div_-10128&Nam=&id=176
# # no vi 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_Hinh_anh_cong_huong_tu_mot_so_truong_hop_nhiem_ky_sinh_trung_nao_hiem_gap_tai_Benh_vien_Dai_hoc_Y_Duoc_Hue__div_-10122&Nam=&id=175
# # no content 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Bien_chung_tim_o_benh_nhan_cuong_giap-10102&Nam=&id=175
# # no content 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NGHIEN_CUU_DAI_THAO_DUONG_TIP_LADA_QUA_156_TRUONG_HOP_DAI_THAO_DUONG_KHONG_THUA_CAN__BEO_PHI_TUOI___35-9299&Nam=&id=155
# # no content 
# ---------
# http://jmp.huemed-univ.edu.vn/View.aspx?idbb=NONG_DO_ESTRADIOL_VA_TESTOSTERON_HUYET_THANH_O_PHU_NU_MAN_KINH-9296&Nam=&id=155
# # no content 
# ---------


# ====================================================================================
# to check:  53 pairs
#  [55, 63, 213, 241, 245,
#  315, 317, 390, 402, 421, 
#  429, 440, 441, 451, 452, 
#  465, 472, 484, 499, 550, checked.

# need to check below
#  621, 638, 639, 640, 644, 
#  645, 646, 648, 649, 650,
#  663, 665, 666, 667, 719,

#  801, 884, 903, 913, 915,
#  958, 962, 970, 

# 1011, 1016, 1102, 1107, 1179, 
# 1188, 1206, 1217, 1222, 1224]
# ===========
# not_found: 110 - link died.
# 259 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=BIEU_HIEN_HOAT_TINH_NATTOKINASE_CUA_CHUNG_BACILLUS_SUBTILIS_C10_TRONG_VECTOR_pHT43-0&Nam=&id=197
# 500 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 501 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 502 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 503 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 504 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 505 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 506 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 508 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 509 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 510 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 511 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 512 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 513 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 514 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=1201
# 525 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_khang_the_khang_cardiolipin_va_khang_β2_glycoprotein_I_o_benh_nhan_lupus_ban_do_he_thong-9704&Nam=2016&id=170
# 592 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div__div_NGHIEN_CUU_TINH_HINH_KHAM_CHUA_BENH_TAI_BENH_VIEN_Y_HOC_CO_TRUYEN_TINH_BINH_ÐINH_NAM_2012-2013__div___div_-10219&Nam=&id=179
# 596 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_ÐANH_GIA_TAC_DUNG_CUA_CHAM_CUU_TREN_NHIP_TIM_O_BENH_NHAN_CUONG_GIAP__div_-10214&Nam=&id=179
# 608 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=_div_XAY_DUNG_QUY_TRINH_DINH_LUONG_POLYSACCHARID_DANG_β-GLUCAN_TRONG_BACH_PHUC_LINH__PORIA_C0C0S_WOLF.___div_-10225&Nam=&id=179
# 626 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 627 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 628 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 629 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 630 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 631 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 632 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 633 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 634 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 635 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 636 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-0&Nam=&id=202
# 658 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_hieu_qua_giam_ðau_trong_ðieu_tri_ðau_that_lung_do_thoai_hoa_cot_song_bang_thuy_cham_ket_hop_thuoc_y_hoc_co_truyen-9565&Nam=2014&id=169
# 839 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Vai_tro_cua_nghiem_phap_kich_thich__β_HCG__trong_chan_doan_chuc_nang__noi_tiet_cua_tinh_hoan_khong_xuong_biu_o_tre_em-9151&Nam=2013&id=147
# 911 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_hieu_chinh_boi_so_trung_vi_PAPP-A_VA_β-hCG_tu_do_trong_huyet_thanh_thai_phu_sang_loc_truoc_sinh_quy_I_tai_benh_vien_Dai_hoc_Y_Duoc_Hue-9448&Nam=2013&id=164
# 935 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9286&Nam=2013&id=153
# 936 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9287&Nam=2013&id=153
# 937 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9270&Nam=2013&id=153
# 938 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9271&Nam=&id=153
# 939 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9275&Nam=2013&id=153
# 940 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9276&Nam=2013&id=153
# 941 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9277&Nam=2013&id=153
# 942 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9272&Nam=2013&id=153
# 943 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9273&Nam=2013&id=153
# 944 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9274&Nam=2013&id=153
# 945 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9279&Nam=2013&id=153
# 946 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9280&Nam=2013&id=153
# 947 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9281&Nam=2013&id=153
# 948 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9282&Nam=2013&id=153
# 949 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9283&Nam=2013&id=153
# 950 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9284&Nam=2013&id=153
# 981 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=Nghien_cuu_su_lien_quan_giua_mot_so_thang_diem_dot_quy_va_nong_do_PAI-1__TNFα_huyet_tuong_o_benh_nhan_nhoi_mau_nao_giai_doan_cap-9429&Nam=2012&id=162
# 1050 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9265&Nam=2012&id=152
# 1051 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9267&Nam=2012&id=152
# 1052 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9266&Nam=2012&id=152
# 1053 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9268&Nam=2012&id=152
# 1054 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9269&Nam=2012&id=152
# 1055 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9254&Nam=2012&id=152
# 1056 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9243&Nam=2012&id=152
# 1057 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9244&Nam=2012&id=152
# 1058 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9245&Nam=2012&id=152
# 1059 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9246&Nam=2012&id=152
# 1060 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9248&Nam=2012&id=152
# 1061 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9247&Nam=2012&id=152
# 1062 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9249&Nam=2012&id=152
# 1063 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9252&Nam=2012&id=152
# 1064 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9250&Nam=2012&id=152
# 1065 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9251&Nam=2012&id=152
# 1066 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9253&Nam=2012&id=152
# 1067 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9255&Nam=2012&id=152
# 1068 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9258&Nam=2012&id=152
# 1069 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9256&Nam=2012&id=152
# 1070 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9257&Nam=2012&id=152
# 1071 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9259&Nam=2012&id=152
# 1072 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9261&Nam=2012&id=152
# 1073 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9260&Nam=2012&id=152
# 1074 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9262&Nam=2012&id=152
# 1075 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9264&Nam=2012&id=152
# 1076 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9263&Nam=2012&id=152
# 1077 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9224&Nam=2012&id=151
# 1078 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9225&Nam=2012&id=151
# 1079 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9228&Nam=2012&id=151
# 1080 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9229&Nam=2012&id=151
# 1081 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9230&Nam=2012&id=151
# 1082 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9231&Nam=2012&id=151
# 1083 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9232&Nam=2012&id=151
# 1084 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9233&Nam=2012&id=151
# 1085 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9234&Nam=2012&id=151
# 1086 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9235&Nam=2012&id=151
# 1087 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9237&Nam=2012&id=151
# 1088 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9236&Nam=2012&id=151
# 1089 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9239&Nam=2012&id=151
# 1090 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9240&Nam=2012&id=151
# 1091 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9241&Nam=2012&id=151
# 1092 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9242&Nam=2012&id=151
# 1093 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9209&Nam=2012&id=151
# 1094 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9208&Nam=2012&id=151
# 1095 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9210&Nam=2012&id=151
# 1096 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9223&Nam=2012&id=151
# 1097 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9226&Nam=2012&id=151
# 1098 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9238&Nam=2012&id=151
# 1099 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9227&Nam=2012&id=151
# 1100 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9211&Nam=2012&id=151
# 1101 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9212&Nam=2012&id=151
# 1103 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9215&Nam=2012&id=151
# 1104 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9214&Nam=2012&id=151
# 1105 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9216&Nam=2012&id=151
# 1106 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9218&Nam=2012&id=151
# 1108 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9219&Nam=2012&id=151
# 1109 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9221&Nam=2012&id=151
# 1110 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9220&Nam=2012&id=151
# 1111 :   http://jmp.huemed-univ.edu.vn/View.aspx?idbb=-9222&Nam=2012&id=151