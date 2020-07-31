# coding=utf-8

from odoo import models, fields, api
import json
import datetime
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        ret = super(SaleOrder, self).create(vals)
        user_id = vals.get('user_id', None)
        # wxcorp_user_id = self.env['res.users'].browse(user_id).partner_id.wxcorp_user_id
        wxcorp_user_id = self.env['res.users'].browse(user_id).partner_id.wx_name
        if wxcorp_user_id:
            self.env['wx.confirm'].sale_order_sent(wxcorp_user_id, ret)
            return ret
        else:
            return ret

class WxConfirm(models.TransientModel):

    _name = 'wx.confirm'
    _description = u'确认'

    info = fields.Text("信息")
    model = fields.Char('模型')
    method = fields.Char('方法')

    @api.multi
    def execute(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)()
        return ret

    @api.multi
    def execute_with_info(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)(self.info)
        return ret

    def sale_order_sent(self, record_ids, ret_dict):
        sale_order = self.env['sale.order'].search([('date_order', '=', ret_dict.date_order)], limit=1)
        sale_order_id = sale_order.id
        sale_order_amount_total = sale_order.amount_total
        sale_order_user_id = sale_order.user_id.partner_id.name
        sale_order_create_uid = sale_order.create_uid.partner_id.name
        sale_order_date_order = ret_dict.date_order.strftime('%Y/%m/%d')
        corp_sales_adress = self.env["wx.corp.config"].search([]).mapped("corp_sales_adress")[0]
        if not corp_sales_adress:
            raise ValidationError('销售订单网址未填写或格式错误')
        info_str = "你有新的报价单\n" + \
                   "订单号：" + ret_dict.name + \
                   "\n订单日期：" + sale_order_date_order + \
                   "\n客户：" + ret_dict.partner_id.name + \
                   "\n销售员：" + sale_order_user_id+ \
                   "\n创建人：" + sale_order_create_uid + \
                   "\n订单金额：" + str(sale_order_amount_total) + \
                   "\n备注：" + ret_dict.note + \
                   "\n订单网址：" + corp_sales_adress.format(sale_order_id)

        ret = self.send_text(record_ids, info_str)
        return ret

    @api.multi
    def send_text(self, wn_name, text):
        from wechatpy.exceptions import WeChatClientException
        #Param = self.env['ir.config_parameter'].sudo()

        try:
            entry = self.env['wx.corp.config'].corpenv()
            # entry.client.message.send_text(entry.current_agent, obj.userid, text)
            entry.client.message.send_text(entry.current_agent, wn_name, text)
        except WeChatClientException as e:
            _logger.info(u'微信消息发送失败 %s'%e)
            raise UserError(u'发送失败 %s'%e)

    @api.model
    def sync_from_remote(self, department_id=1):
        '''
        从企业微信通讯录同步
        '''
        from wechatpy.exceptions import WeChatClientException
        try:
            entry = self.env['wx.corp.config'].corpenv()
            config = self.env['wx.corp.config'].sudo().get_cur()
            if not config.Corp_Id:
                raise ValidationError(u'尚未做企业微信对接配置')
            users = entry.txl_client.user.list(department_id, fetch_child=True)
            for info in users:
                rs = self.env['res.partner'].search([('mobile', '=', info['mobile'])], limit=1).id
                if rs:
                    res_partner = {
                        'wx_name': info['userid']
                    }
                    self.sudo().env['res.partner'].browse(rs).write(res_partner)
        except WeChatClientException as e:
            raise ValidationError(u'微信服务请求异常，异常码: %s 异常信息: %s' % (e.errcode, e.errmsg))

    @api.multi
    def sync_from_remote_confirm(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此操作可能需要一定时间，确认同步吗？"
        new_context['default_model'] = 'wx.confirm'
        new_context['default_method'] = 'sync_from_remote'
        return {
            'name': u'确认同步已有企业微信用户至本系统',
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('yfc_wx.wx_confirm_view_form').id,
            'target': 'new'
        }



class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')



