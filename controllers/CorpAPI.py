import sys
import os
import re

import json
import requests

# sys.path.append("../../")
#
# from conf import DEBUG

DEBUG = False
CORP_API_TYPE = {
        'GET_ACCESS_TOKEN' : ['/cgi-bin/gettoken', 'GET'],
        'USER_CREATE' 	   : ['/cgi-bin/user/create?access_token=ACCESS_TOKEN', 'POST'],
        'USER_GET' 	   : ['/cgi-bin/user/get?access_token=ACCESS_TOKEN', 'GET'],
        'USER_UPDATE'      : ['/cgi-bin/user/update?access_token=ACCESS_TOKEN', 'POST'],
        'USER_DELETE' 	   : ['/cgi-bin/user/delete?access_token=ACCESS_TOKEN', 'GET'],
        'USER_BATCH_DELETE': ['/cgi-bin/user/batchdelete?access_token=ACCESS_TOKEN', 'POST'],
        'USER_SIMPLE_LIST ': ['/cgi-bin/user/simplelist?access_token=ACCESS_TOKEN', 'GET'],
        'USER_LIST' 	   : ['/cgi-bin/user/list?access_token=ACCESS_TOKEN', 'GET'],
        'USERID_TO_OPENID' : ['/cgi-bin/user/convert_to_openid?access_token=ACCESS_TOKEN', 'POST'],
        'OPENID_TO_USERID' : ['/cgi-bin/user/convert_to_userid?access_token=ACCESS_TOKEN', 'POST'],
        'USER_AUTH_SUCCESS': ['/cgi-bin/user/authsucc?access_token=ACCESS_TOKEN', 'GET'],

        'DEPARTMENT_CREATE': ['/cgi-bin/department/create?access_token=ACCESS_TOKEN', 'POST'],
        'DEPARTMENT_UPDATE': ['/cgi-bin/department/update?access_token=ACCESS_TOKEN', 'POST'],
        'DEPARTMENT_DELETE': ['/cgi-bin/department/delete?access_token=ACCESS_TOKEN', 'GET'],
        'DEPARTMENT_LIST'  : ['/cgi-bin/department/list?access_token=ACCESS_TOKEN', 'GET'],

        'TAG_CREATE' 	   : ['/cgi-bin/tag/create?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_UPDATE' 	   : ['/cgi-bin/tag/update?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_DELETE'  	   : ['/cgi-bin/tag/delete?access_token=ACCESS_TOKEN', 'GET'],
        'TAG_GET_USER' 	   : ['/cgi-bin/tag/get?access_token=ACCESS_TOKEN', 'GET'],
        'TAG_ADD_USER' 	   : ['/cgi-bin/tag/addtagusers?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_DELETE_USER'  : ['/cgi-bin/tag/deltagusers?access_token=ACCESS_TOKEN', 'POST'],
        'TAG_GET_LIST' 	   : ['/cgi-bin/tag/list?access_token=ACCESS_TOKEN', 'GET'],

        'BATCH_JOB_GET_RESULT' : ['/cgi-bin/batch/getresult?access_token=ACCESS_TOKEN', 'GET'],

        'BATCH_INVITE'     : ['/cgi-bin/batch/invite?access_token=ACCESS_TOKEN', 'POST'],

        'AGENT_GET' 	   : ['/cgi-bin/agent/get?access_token=ACCESS_TOKEN', 'GET'],
        'AGENT_SET' 	   : ['/cgi-bin/agent/set?access_token=ACCESS_TOKEN', 'POST'],
        'AGENT_GET_LIST'   : ['/cgi-bin/agent/list?access_token=ACCESS_TOKEN', 'GET'],

        'MENU_CREATE' : ['/cgi-bin/menu/create?access_token=ACCESS_TOKEN', 'POST'], ## TODO
        'MENU_GET' 	   : ['/cgi-bin/menu/get?access_token=ACCESS_TOKEN', 'GET'],
        'MENU_DELETE' 	   : ['/cgi-bin/menu/delete?access_token=ACCESS_TOKEN', 'GET'],

        'MESSAGE_SEND' 	   : ['/cgi-bin/message/send?access_token=ACCESS_TOKEN', 'POST'],

        'MEDIA_GET' 	   : ['/cgi-bin/media/get?access_token=ACCESS_TOKEN', 'GET'],

        'GET_USER_INFO_BY_CODE' : ['/cgi-bin/user/getuserinfo?access_token=ACCESS_TOKEN', 'GET'],
        'GET_USER_DETAIL'  : ['/cgi-bin/user/getuserdetail?access_token=ACCESS_TOKEN', 'POST'],

        'GET_TICKET' 	   : ['/cgi-bin/ticket/get?access_token=ACCESS_TOKEN', 'GET'],
        'GET_JSAPI_TICKET' : ['/cgi-bin/get_jsapi_ticket?access_token=ACCESS_TOKEN', 'GET'],

        'GET_CHECKIN_OPTION' : ['/cgi-bin/checkin/getcheckinoption?access_token=ACCESS_TOKEN', 'POST'],
        'GET_CHECKIN_DATA' : ['/cgi-bin/checkin/getcheckindata?access_token=ACCESS_TOKEN', 'POST'],
        'GET_APPROVAL_DATA': ['/cgi-bin/corp/getapprovaldata?access_token=ACCESS_TOKEN', 'POST'],

        'GET_INVOICE_INFO' : ['/cgi-bin/card/invoice/reimburse/getinvoiceinfo?access_token=ACCESS_TOKEN', 'POST'],
        'UPDATE_INVOICE_STATUS' :
            ['/cgi-bin/card/invoice/reimburse/updateinvoicestatus?access_token=ACCESS_TOKEN', 'POST'],
        'BATCH_UPDATE_INVOICE_STATUS' :
            ['/cgi-bin/card/invoice/reimburse/updatestatusbatch?access_token=ACCESS_TOKEN', 'POST'],
        'BATCH_GET_INVOICE_INFO' :
            ['/cgi-bin/card/invoice/reimburse/getinvoiceinfobatch?access_token=ACCESS_TOKEN', 'POST'],
}


class ApiException(Exception):
    def __init__(self, errCode, errMsg):
        self.errCode = errCode
        self.errMsg = errMsg


class AbstractApi(object):
    def __init__(self):
        return

    def getAccessToken(self):
        raise NotImplementedError

    def refreshAccessToken(self):
        raise NotImplementedError

    def getSuiteAccessToken(self):
        raise NotImplementedError

    def refreshSuiteAccessToken(self):
        raise NotImplementedError

    def getProviderAccessToken(self):
        raise NotImplementedError

    def refreshProviderAccessToken(self):
        raise NotImplementedError

    def httpCall(self, urlType, args=None):
        shortUrl = urlType[0]
        method = urlType[1]
        response = {}
        for retryCnt in range(0, 3):
            if 'POST' == method:
                url = self.__makeUrl(shortUrl)
                response = self.__httpPost(url, args)
            elif 'GET' == method:
                url = self.__makeUrl(shortUrl)
                url = self.__appendArgs(url, args)
                response = self.__httpGet(url)
            else:
                raise ApiException(-1, "unknown method type")

            # check if token expired
            if self.__tokenExpired(response.get('errcode')):
                self.__refreshToken(shortUrl)
                retryCnt += 1
                continue
            else:
                break
        return self.__checkResponse(response)

    @staticmethod
    def __appendArgs(url, args):
        if args is None:
            return url

        for key, value in args.items():
            if '?' in url:
                url += ('&' + key + '=' + value)
            else:
                url += ('?' + key + '=' + value)
        return url

    @staticmethod
    def __makeUrl(shortUrl):
        base = "https://qyapi.weixin.qq.com"
        if shortUrl[0] == '/':
            return base + shortUrl
        else:
            return base + '/' + shortUrl

    def __appendToken(self, url):
        if 'SUITE_ACCESS_TOKEN' in url:
            return url.replace('SUITE_ACCESS_TOKEN', self.getSuiteAccessToken())
        elif 'PROVIDER_ACCESS_TOKEN' in url:
            return url.replace('PROVIDER_ACCESS_TOKEN', self.getProviderAccessToken())
        elif 'ACCESS_TOKEN' in url:
            return url.replace('ACCESS_TOKEN', self.getAccessToken())
        else:
            return url

    def __httpPost(self, url, args):
        realUrl = self.__appendToken(url)

        if DEBUG is True:
            print(realUrl, args)

        return requests.post(realUrl, data=json.dumps(args).decode('unicode-escape').encode("utf-8")).json()

    def __httpGet(self, url):
        realUrl = self.__appendToken(url)

        if DEBUG is True:
            print(realUrl)

        return requests.get(realUrl).json()

    def __post_file(self, url, media_file):
        return requests.post(url, file=media_file).json()

    @staticmethod
    def __checkResponse(response):
        errCode = response.get('errcode')
        errMsg = response.get('errmsg')

        if errCode == 0:
            return response
        else:
            raise ApiException(errCode, errMsg)

    @staticmethod
    def __tokenExpired(errCode):
        if errCode == 40014 or errCode == 42001 or errCode == 42007 or errCode == 42009:
            return True
        else:
            return False

    def __refreshToken(self, url):
        if 'SUITE_ACCESS_TOKEN' in url:
            self.refreshSuiteAccessToken()
        elif 'PROVIDER_ACCESS_TOKEN' in url:
            self.refreshProviderAccessToken()
        elif 'ACCESS_TOKEN' in url:
            self.refreshAccessToken()





class CorpApi(AbstractApi) :

    def __init__(self, corpid, secret) :
        self.corpid = corpid
        self.secret = secret
        self.access_token = None

    def getAccessToken(self) :
        if self.access_token is None :
            self.refreshAccessToken()
        return self.access_token

    def refreshAccessToken(self) :
        response = self.httpCall(
                CORP_API_TYPE['GET_ACCESS_TOKEN'],
                {
                    'corpid'    :   self.corpid,
                    'corpsecret':   self.secret,
                })
        self.access_token = response.get('access_token')



SERVICE_CORP_API_TYPE = {
        'GET_CORP_TOKEN'    : ['/cgi-bin/service/get_corp_token?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
        'GET_SUITE_TOKEN'   : ['/cgi-bin/service/get_suite_token', 'POST'],
        'GET_PRE_AUTH_CODE' : ['/cgi-bin/service/get_pre_auth_code?suite_access_token=SUITE_ACCESS_TOKEN', 'GET'],
        'SET_SESSION_INFO'  : ['/cgi-bin/service/set_session_info?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
        'GET_PERMANENT_CODE': ['/cgi-bin/service/get_permanent_code?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
        'GET_AUTH_INFO'     : ['/cgi-bin/service/get_auth_info?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
        'GET_ADMIN_LIST'    : ['/cgi-bin/service/get_admin_list?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
        'GET_USER_INFO_BY_3RD' : ['/cgi-bin/service/getuserinfo3rd?suite_access_token=SUITE_ACCESS_TOKEN', 'GET'],
        'GET_USER_DETAIL_BY_3RD' : ['/cgi-bin/service/getuserdetail3rd?suite_access_token=SUITE_ACCESS_TOKEN', 'POST'],
}



class ServiceCorpApi(CorpApi) :
    def __init__(self, suite_id, suite_secret, suite_ticket, auth_corpid=None, permanent_code=None) :
        self.suite_id = suite_id
        self.suite_secret = suite_secret
        self.suite_ticket = suite_ticket

        # 调用 CorpAPI 的function， 需要设置这两个参数
        self.auth_corpid = auth_corpid
        self.permanent_code = permanent_code

        self.access_token = None
        self.suite_access_token = None

    ## override CorpApi 的 refreshAccessToken， 使用第三方服务商的方法
    def getAccessToken(self) :
        if self.access_token is None :
            self.refreshAccessToken()
        return self.access_token
    def refreshAccessToken(self) :
        response = self.httpCall(
                SERVICE_CORP_API_TYPE['GET_CORP_TOKEN'],
                {
                    "auth_corpid"   : self.auth_corpid,
                    "permanent_code": self.permanent_code,
                })
        self.access_token = response.get('access_token')

    ##
    def getSuiteAccessToken(self) :
        if self.suite_access_token is None :
            self.refreshSuiteAccessToken()
        return self.suite_access_token

    def refreshSuiteAccessToken(self) :
        response = self.httpCall(
                SERVICE_CORP_API_TYPE['GET_SUITE_TOKEN'],
                {
                    "suite_id"      : self.suite_id,
                    "suite_secret"  : self.suite_secret,
                    "suite_ticket"  : self.suite_ticket,
                })
        self.suite_access_token= response.get('suite_access_token')



SERVICE_PROVIDER_API_TYPE = {
        'GET_PROVIDER_TOKEN': ['/cgi-bin/service/get_provider_token', 'POST'],
        'GET_LOGIN_INFO'    : ['/cgi-bin/service/get_login_info?access_token=PROVIDER_ACCESS_TOKEN', 'POST'],
        'GET_REGISTER_CODE' : ['/cgi-bin/service/get_register_code?provider_access_token=PROVIDER_ACCESS_TOKEN', 'POST'],
        'GET_REGISTER_INFO' : ['/cgi-bin/service/get_register_info?provider_access_token=PROVIDER_ACCESS_TOKEN', 'POST'],
        'SET_AGENT_SCOPE'   : ['/cgi-bin/agent/set_scope', 'POST'], ### TODO
        'SET_CONTACT_SYNC_SUCCESS' : ['/cgi-bin/sync/contact_sync_success', 'GET'],
}

class ServiceProviderApi(AbstractApi) :
    def __init__(self, corpid, provider_secret) :
        self.corpid = corpid
        self.provider_secret = provider_secret

        self.provider_access_token = None

    def getProviderAccessToken(self) :
        if self.provider_access_token is None :
            self.refreshProviderAccessToken()
        return self.provider_access_token

    def refreshProviderAccessToken(self) :
        response = self.httpCall(
                SERVICE_PROVIDER_API_TYPE['GET_PROVIDER_TOKEN'],
                {
                    'corpid'         :   self.corpid,
                    'provider_secret':   self.provider_secret,
                })
        self.provider_access_token = response.get('provider_access_token')

