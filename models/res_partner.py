# coding=utf-8
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'
    wxcorp_user_id = fields.Many2one('wx.corpuser','关联企业号用户')
    # wx_user_id = fields.Many2one('wx.user','关联微信用户')
    wx_name = fields.Char(string='企业微信账户', store=True, default=None)

    @api.multi
    def send_text(self, text):
        from wechatpy.exceptions import WeChatClientException
        Param = self.env['ir.config_parameter'].sudo()
        for obj in self:
            try:
                entry = self.env['wx.corp.config'].corpenv()
                
                # entry.client.message.send_text(entry.current_agent, obj.userid, text)
                entry.client.message.send_text(entry.current_agent, obj.wx_name, text)
            except WeChatClientException as e:
                _logger.info(u'微信消息发送失败 %s'%e)
                raise UserError(u'发送失败 %s'%e)

    def send_corp_msg(self, msg):
        entry = self.env['wx.corp.config'].corpenv()
        self = self.sudo()
        mtype = msg["mtype"]
        if mtype=="text":
            entry.client.message.send_text(entry.current_agent, self.wxcorp_user_id.userid, msg["content"])
        if mtype=="card":
            entry.client.message.send_text_card(entry.current_agent, self.wxcorp_user_id.userid, msg['title'], msg['description'], msg['url'], btntxt=msg.get("btntxt", "详情"))
        elif mtype=='image':
            ret = entry.client.media.upload(mtype, msg['media_data'])
            entry.client.message.send_image(entry.current_agent, self.wxcorp_user_id.userid, ret['media_id'])
        elif mtype=='voice':
            ret = entry.client.media.upload(mtype, msg['media_data'])
            entry.client.message.send_voice(entry.current_agent, self.wxcorp_user_id.userid, ret['media_id'])

    def get_corp_key(self):
        self = self.sudo()
        if self.wxcorp_user_id:
            return self.wxcorp_user_id.userid

    # def get_wx_key(self):
    #     self = self.sudo()
    #     if self.wx_user_id:
    #         return self.wx_user_id.openid
