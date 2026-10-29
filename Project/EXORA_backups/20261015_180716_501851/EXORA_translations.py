"""คำแปลหน้าจอ English / 简体中文; ภาษาไทยเป็นข้อความต้นฉบับ."""
DATA='''
หน้าร้าน|Storefront|店铺首页
แลกเปลี่ยนเงิน|Currency exchange|货币兑换
ประวัติรายการ|Transaction history|交易记录
โปรไฟล์ของฉัน|My profile|我的资料
ติดต่อร้าน|Contact store|联系店铺
ตรวจสอบรายการ|Review transactions|审核交易
ตรวจสอบสลิป|Review payment proof|审核付款凭证
สถิติรายการ|Transaction statistics|交易统计
จัดการร้าน|Store management|店铺管理
กลับฝั่งแอดมิน|Back to admin|返回管理员页面
ดูหน้าผู้ใช้|Preview customer view|预览用户页面
โหมดดูตัวอย่าง · บัญชีของคุณ|Preview · your account|预览模式 · 您的账户
โหมดดูหน้าผู้ใช้แสดงเฉพาะรายการของบัญชีคุณ|Customer preview shows only your own transactions|用户预览仅显示您自己的交易
นี่คือโหมดดูหน้าผู้ใช้ กลับฝั่งแอดมินเพื่อบันทึกข้อมูล|Return to admin view to save changes|请返回管理员页面保存更改
เอฟเฟกต์|Animations|动画效果
ออกจากระบบ|Sign out|退出登录
ยินดีต้อนรับกลับ|Welcome back|欢迎回来
ชื่อผู้ใช้ หรืออีเมล|Username or email|用户名或邮箱
ชื่อผู้ใช้|Username|用户名
รหัสผ่านปัจจุบัน|Current password|当前密码
รหัสผ่านใหม่อย่างน้อย 8 ตัว|New password (at least 8 characters)|新密码（至少8个字符）
รหัสผ่านอย่างน้อย 8 ตัว|Password (at least 8 characters)|密码（至少8个字符）
ยืนยันรหัสผ่านใหม่|Confirm new password|确认新密码
ยืนยันรหัสผ่าน|Confirm password|确认密码
รหัสผ่านใหม่ไม่ตรงกัน|New passwords do not match|新密码不一致
รหัสผ่านไม่ตรงกัน|Passwords do not match|密码不一致
รหัสผ่าน|Password|密码
เข้าสู่ระบบ|Sign in|登录
ยังไม่มีบัญชี?  สมัครสมาชิก|New here? Create an account|还没有账户？注册
ลืมรหัสผ่าน?  รับ OTP ทางอีเมล|Forgot password? Email verification|忘记密码？邮箱验证
สร้างบัญชี|Create account|创建账户
เริ่มต้นการเดินทางของคุณ|Start your journey|开启您的旅程
กลับเข้าสู่การเดินทางของคุณ|Continue your journey|继续您的旅程
เตรียมพร้อมสำหรับทุกการเดินทาง|Ready for every journey|为每次旅程做好准备
ข้อมูลเข้าสู่ระบบไม่ถูกต้อง หรือบัญชีถูกจำกัดชั่วคราว กรุณาตรวจสอบหรือลองภายหลัง|Invalid credentials or temporarily restricted account. Check your details or try later.|登录信息错误或账户暂时受限。请检查信息或稍后重试。
บัญชีนี้ไม่พร้อมใช้งาน กรุณาติดต่อร้าน|Account unavailable. Please contact the store.|账户不可用，请联系店铺。
กรุณาเปลี่ยนรหัสผ่าน admin เริ่มต้นก่อนจัดการร้านหรือทำรายการ|Change the default admin password before managing the store or making transactions|请先修改管理员默认密码，再管理店铺或进行交易
กรุณาเปลี่ยนรหัสผ่าน admin เริ่มต้นก่อน|Change the default admin password first|请先修改管理员默认密码
ยืนยัน OTP และตั้งรหัสผ่านใหม่|Verify OTP and reset password|验证验证码并重置密码
อีเมลที่ลงทะเบียน|Registered email|注册邮箱
OTP 6 หลัก|6-digit OTP|6位验证码
ส่ง OTP ไปยังอีเมล|Email verification code|发送邮箱验证码
ส่ง / ขอ OTP ใหม่|Send / resend OTP|发送／重新发送验证码
กำลังส่ง OTP…|Sending OTP…|正在发送验证码…
กรุณาขอ OTP ก่อน|Request an OTP first|请先获取验证码
อีเมลเปลี่ยนแล้ว กรุณาขอ OTP สำหรับอีเมลนี้ใหม่|Email changed. Request a new OTP.|邮箱已更改，请重新获取验证码。
ตั้งรหัสผ่านใหม่แล้ว กรุณาเข้าสู่ระบบด้วยรหัสใหม่|Password reset. Sign in with your new password.|密码已重置，请使用新密码登录。
เปลี่ยนรหัสผ่านแล้ว|Password changed|密码已修改
เปลี่ยนรหัสผ่าน|Change password|修改密码
คำนวณเงิน|Currency calculator|兑换计算器
จำนวนเงินที่ต้องการแลก|Amount to exchange|兑换金额
จากสกุลเงิน|From currency|原币种
เป็นสกุลเงิน|To currency|目标币种
เลือกสกุลเงิน แล้วคำนวณยอด|Choose currencies, then calculate|选择币种后计算
คำนวณยอดใหม่หลังเปลี่ยนข้อมูล|Recalculate after changing details|更改信息后请重新计算
คำนวณยอด|Calculate|计算金额
ทำรายการและแนบสลิป|Continue and submit payment proof|继续交易并上传凭证
สลับสกุลเงิน|Swap currencies|交换币种
ยอดเงินลัด|Quick amounts|快捷金额
เลือกสกุลเงินสำหรับการเดินทาง|Choose your currency|选择货币
ราคาซื้อ–ขายของร้าน · THB ต่อ 1 หน่วย|Store buy / sell rates · THB per 1 unit|店铺买入／卖出价 · 每单位泰铢价格
รายการโปรดเท่านั้น|Favorites only|仅显示收藏
ยังไม่มีรายการโปรด · กด ☆ บนการ์ดเพื่อเพิ่ม|No favorites yet · select ☆ to add|暂无收藏 · 点击卡片上的 ☆ 添加
อัปเดตค่าเงินทันที|Refresh rates now|立即更新汇率
เลือกคำนวณ|Use in calculator|选择并计算
ร้านรับซื้อ|Store buys|店铺买入
ร้านขาย|Store sells|店铺卖出
รอตั้งราคา|Rate not set|尚未定价
ข้อมูลอ้างอิง|Reference data|参考数据
กำลังตรวจสอบราคาออนไลน์…|Checking online rates…|正在查询在线汇率…
ยังอัปเดตไม่ได้ · ใช้ราคาล่าสุดที่บันทึกไว้|Update unavailable · using last saved rates|暂时无法更新 · 使用上次保存的汇率
ดึงข้อมูลไม่สำเร็จ · ใช้ราคาที่บันทึกไว้|Refresh failed · using saved rates|获取失败 · 使用已保存的汇率
กำลังตรวจสอบ|Checking|正在检查
ข้อมูลเดิม|Saved data|已保存数据
อัตราอ้างอิงรายวัน|Daily reference rates|每日参考汇率
อัตราแลกเปลี่ยนของร้าน|Store exchange rates|店铺汇率
อัตราแลกเปลี่ยน|Exchange rates|汇率
ตรวจสอบราคาออนไลน์|Refresh online rates|查询在线汇率
THB ต่อ 1 หน่วย|THB per 1 unit|每单位泰铢价格
อ้างอิงออนไลน์|Online reference|在线参考价
รับซื้อ|Buy|买入
ขาย|Sell|卖出
ชำระและส่งมอบเงิน|Payment and currency handover|付款与货币交付
วิธีชำระและส่งมอบเงิน|Payment and handover method|付款与交付方式
วิธีชำระเงิน|Payment method|付款方式
ชื่อลูกค้า|Customer name|客户姓名
ชำระด้วยบัตร|Card payment|银行卡付款
บัตรเครดิต / เดบิต|Credit / debit card|信用卡／借记卡
บัตรเครดิต/เดบิต|Credit / debit card|信用卡／借记卡
ช่องทางบัตรยังไม่เปิดบริการ|Card payments are not available yet|暂未开通银行卡付款
ยังไม่เปิดบริการ|Not available yet|尚未开放
QR พร้อมเพย์|PromptPay QR|PromptPay二维码
เปิด QR ขนาดเต็ม|View full-size QR|查看完整二维码
ยังไม่มี QR ร้าน|Store QR not available|店铺二维码尚未设置
ไม่พบ QR กรุณาติดต่อร้าน|QR unavailable. Contact the store.|未找到二维码，请联系店铺。
โอนบัญชีธนาคาร|Bank transfer|银行转账
โอนธนาคาร|Bank transfer|银行转账
บัญชีร้านที่รับเงิน|Store receiving account|店铺收款账户
ร้านยังไม่ได้ตั้งบัญชีรับเงิน|Store receiving account is not set|店铺尚未设置收款账户
ธนาคารที่ใช้โอน|Sender bank|转出银行
เลือกธนาคาร|Select bank|选择银行
ชื่อบัญชีผู้โอน|Sender account name|付款账户姓名
เลขบัญชีผู้โอน|Sender account number|付款账号
ยอดโอน (THB)|Transfer amount (THB)|转账金额（THB）
วันเวลาโอน (YYYY-MM-DD HH:MM)|Transfer time (YYYY-MM-DD HH:MM)|转账时间（YYYY-MM-DD HH:MM）
เลขอ้างอิง (ถ้ามี)|Reference number (optional)|参考编号（可选）
ราคานี้ใช้ได้ถึง|Quote valid until|报价有效至
หลักฐานการชำระเงิน|Payment proof|付款凭证
ยังไม่ได้แนบสลิป|No payment proof attached|尚未上传付款凭证
แนบสลิป JPG / PNG ไม่เกิน 10 MB|Attach JPG / PNG proof, up to 10 MB|上传JPG／PNG凭证，不超过10MB
แนบสลิปใหม่|Replace payment proof|更换付款凭证
แนบสลิป|Attach payment proof|上传付款凭证
ส่งหลักฐานให้เจ้าหน้าที่ตรวจสอบ|Submit proof for review|提交凭证等待审核
ส่งมอบเงินต่างประเทศที่ร้าน|Hand over foreign currency at store|到店交付外币
ส่งมอบเงินที่หน้าร้าน|Hand over currency at store|到店交付货币
บันทึกรายการส่งมอบเงินที่ร้าน|Submit in-store handover|提交到店交付记录
บันทึกรายการรอตรวจสอบการส่งมอบเงินที่ร้านแล้ว|In-store handover submitted for review|到店交付记录已提交审核
บันทึกรายการรอตรวจสอบแล้ว|Transaction submitted for review|交易已提交审核
กรุณาเพิ่มเบอร์โทรในโปรไฟล์ก่อนทำรายการ|Add your phone number to your profile first|请先在资料中添加电话号码
กรุณาแนบสลิป|Attach payment proof first|请先上传付款凭证
กรุณาเลือกธนาคารผู้โอน|Select the sender bank|请选择转出银行
ได้รับ|You receive|您将收到
แลกจาก|Exchange from|兑换原币
ประวัติจากระบบเดิม|Imported history|旧系统记录
ประวัติเดิม|Legacy records|历史记录
ดูรายละเอียด / สลิป / PDF|Details / proof / PDF|详情／凭证／PDF
ค้นหา / รีเฟรช|Search / refresh|搜索／刷新
ทุกสถานะ|All statuses|所有状态
รอตรวจสอบ|Pending review|待审核
อนุมัติแล้ว|Approved|已批准
ปฏิเสธรายการ|Reject transaction|拒绝交易
ปฏิเสธ|Rejected|已拒绝
อนุมัติรายการ|Approve transaction|批准交易
อนุมัติ|Approve|批准
ตรวจสอบเมื่อ|Reviewed at|审核时间
จำนวนเงินโอน|Transfer amount|转账金额
ธนาคาร / ชื่อผู้โอน|Bank / sender|银行／付款人
โอนเมื่อ / อ้างอิง|Transfer time / reference|转账时间／参考编号
ระบุเหตุผลที่ปฏิเสธ|Reason for rejection|拒绝原因
ตรวจสอบสลิปโดยเจ้าหน้าที่|Payment proof reviewed by staff|工作人员审核付款凭证
ตรวจสอบการส่งมอบเงินต่างประเทศที่ร้านแล้ว|Foreign currency handover checked at store|已核实到店外币交付
รายการนี้ไม่มีภาพสลิป|This transaction has no payment image|此交易没有付款凭证图片
เปิดสลิปขนาดเต็ม|View full-size proof|查看完整凭证
ภาพสลิป|Payment proof image|付款凭证图片
ส่งใบเสร็จทางอีเมล|Email receipt|发送电子收据
กำลังส่งใบเสร็จ…|Sending receipt…|正在发送收据…
กำลังสร้าง PDF และส่งอีเมล|Creating PDF and sending email|正在生成PDF并发送邮件
ส่งใบเสร็จพร้อม PDF ไปยัง|Send receipt and PDF to|发送收据与PDF至
บันทึก PDF แล้ว|PDF saved|PDF已保存
บันทึก PDF|Save PDF|保存PDF
สร้างใบเสร็จธีม EXORA แล้ว กดส่งใบเสร็จในรายละเอียดเพื่อส่งให้ผู้ทำรายการ|EXORA receipt created. Send it from transaction details.|EXORA收据已生成，可在交易详情中发送。
ใบเสร็จอัตโนมัติ:|Automatic receipt:|自动收据：
ยังไม่มีอีเมลในโปรไฟล์|No email in profile|资料中没有邮箱
ให้ผู้ทำรายการเพิ่มอีเมลในโปรไฟล์ก่อนส่งใบเสร็จ|The customer must add an email before sending the receipt|发送收据前，客户须在资料中添加邮箱
ไม่พบบัญชีผู้ทำรายการ|Transaction owner not found|未找到交易账户
ผู้ส่ง:|Sender:|发件人：
ส่งไปที่:|Recipient:|收件人：
พร้อมส่ง OTP / ใบเสร็จ|Ready for OTP / receipts|可发送验证码／收据
ยังไม่ได้ตั้ง Gmail App Password|Gmail App Password is not configured|尚未设置Gmail应用专用密码
ระบบอีเมลยังไม่พร้อม กรุณาติดต่อร้าน|Email service unavailable. Contact the store.|邮件服务不可用，请联系店铺。
ส่งไม่สำเร็จ|Send failed|发送失败
ส่งแล้ว|Sent|已发送
กำลังส่ง|Sending|正在发送
ข้อมูลส่วนตัว|Personal details|个人资料
ชื่อที่แสดง|Display name|显示名称
รูปโปรไฟล์|Profile picture|头像
เลือกรูปโปรไฟล์|Choose profile picture|选择头像
บันทึกโปรไฟล์แล้ว|Profile saved|资料已保存
บันทึกโปรไฟล์|Save profile|保存资料
เลือกสีร้าน|Choose store color|选择店铺颜色
เลือกสี|Choose color|选择颜色
ข้อมูลติดต่อร้าน|Store contact details|店铺联系方式
ร้านยังไม่ได้เพิ่มข้อมูลติดต่อ|Store contact details are not set|店铺尚未添加联系方式
บันทึกข้อมูลติดต่อร้านแล้ว|Store contact details saved|店铺联系方式已保存
บันทึกข้อมูลติดต่อ|Save contact details|保存联系方式
เปิดแผนที่|Open map|打开地图
เปิดลิงก์|Open link|打开链接
เบอร์โทรร้าน|Store phone|店铺电话
เบอร์โทร|Phone number|电话号码
ที่อยู่|Address|地址
เวลาเปิดบริการ|Opening hours|营业时间
อีเมล|Email|邮箱
ข้อความแนะนำ|Tagline|介绍文字
ชื่อร้าน|Store name|店铺名称
คำแนะนำก่อนแนบสลิป|Payment proof instructions|上传凭证说明
บัญชีธนาคารรับเงิน: ชื่อธนาคาร|Receiving bank name|收款银行名称
ชื่อบัญชีรับเงินของร้าน|Store receiving account name|店铺收款账户姓名
เลขบัญชีรับเงินของร้าน|Store receiving account number|店铺收款账号
บันทึกหน้าร้านแล้ว|Store settings saved|店铺设置已保存
บันทึกหน้าร้าน|Save store settings|保存店铺设置
ใช้ราคาออนไลน์คำนวณราคาซื้อ–ขายอัตโนมัติ|Calculate buy / sell rates automatically from online data|根据在线数据自动计算买入／卖出价
ส่วนต่าง %|Spread %|价差 %
แก้ไขที่เลือก / เพิ่มสกุลเงิน|Edit selected / add currency|编辑所选／添加币种
กรุณาปิดราคาซื้อ–ขายอัตโนมัติก่อนแก้ไขราคาเอง|Disable automatic pricing before editing rates|手动修改汇率前请关闭自动定价
รหัสสกุลเงิน 3 ตัว|3-letter currency code|3位货币代码
ชื่อสกุลเงิน|Currency name|货币名称
ราคาที่ร้านรับซื้อ (THB ต่อ 1 หน่วย)|Store buy rate (THB per unit)|店铺买入价（每单位THB）
ราคาที่ร้านขาย (THB ต่อ 1 หน่วย)|Store sell rate (THB per unit)|店铺卖出价（每单位THB）
บันทึกอัตรา|Save rates|保存汇率
ผู้ใช้งาน|Users|用户
สิทธิ์ผู้ใช้งาน|User permissions|用户权限
จัดการสิทธิ์ที่เลือก|Manage selected account|管理所选账户
บันทึกสิทธิ์|Save permissions|保存权限
ปลดแบน / เปิดใช้งาน|Unban / activate|解除封禁／启用
แบนผู้ใช้|Ban user|封禁用户
ลบผู้ใช้|Delete user|删除用户
ลบบัญชี|Delete account|删除账户
บัญชีจะเข้าใช้งานไม่ได้ โดยเก็บประวัติรายการไว้|The account cannot sign in; transaction history is retained|账户无法登录，但交易记录将保留
ข่าวการเงินโลก · สไลด์หน้าแรก|Global finance news · homepage slides|全球财经新闻 · 首页轮播
ข่าวหน้าแรก|Homepage news|首页新闻
เพิ่มภาพข่าว JPG / PNG ไม่เกิน 10 MB|Add JPG / PNG news image, up to 10 MB|添加JPG／PNG新闻图片，不超过10MB
เพิ่มภาพข่าว|Add news image|添加新闻图片
หัวข้อข่าว (ไม่เกิน 120 ตัวอักษร)|News title (up to 120 characters)|新闻标题（最多120个字符）
หัวข้อข่าว|News title|新闻标题
ลิงก์ข่าวต้นฉบับ (https://... เว้นว่างได้)|Original article URL (https://... optional)|新闻原文链接（https://... 可选）
ลิงก์ข่าวต้นฉบับ (เว้นว่างเพื่อลบลิงก์)|Article URL (leave empty to remove)|新闻链接（留空删除链接）
ลิงก์ข่าว|Article link|新闻链接
บันทึกลิงก์|Save link|保存链接
แก้ไขลิงก์|Edit link|编辑链接
ภาพข่าว JPG / PNG|News image JPG / PNG|新闻图片JPG／PNG
ยังไม่ได้เลือกภาพ|No image selected|尚未选择图片
เลือกภาพข่าว|Choose news image|选择新闻图片
เพิ่มเข้าสไลด์|Add to slideshow|添加到轮播
ลบข่าวนี้ออกจากสไลด์?|Remove this news from the slideshow?|从轮播中删除这条新闻？
ลบข่าว|Delete news|删除新闻
แสดง / ซ่อน|Show / hide|显示／隐藏
การแสดงผล|Visibility|显示状态
แสดง|Visible|显示
ซ่อน|Hidden|隐藏
ขึ้น ↑|Move up ↑|上移 ↑
ลง ↓|Move down ↓|下移 ↓
ลำดับในตารางคือลำดับสไลด์ · ข่าวที่ซ่อนจะไม่แสดง · กลับหน้าแรกเพื่อดูข่าวที่บันทึก|Table order is slide order. Hidden news is excluded. View saved news on the homepage.|表格顺序即轮播顺序。隐藏新闻不显示。返回首页查看已保存新闻。
เปิดลิงก์ข่าวไม่ได้ กรุณาติดต่อแอดมิน|Cannot open the article. Contact admin.|无法打开新闻链接，请联系管理员。
ไม่พบภาพข่าว กรุณาติดต่อแอดมิน|News image missing. Contact admin.|未找到新闻图片，请联系管理员。
ยังไม่มีภาพข่าว|No news image yet|暂无新闻图片
ผู้ทำรายการบ่อยที่สุด|Most active customers|交易最频繁的客户
สกุลเงินยอดนิยม|Popular currencies|热门币种
สรุปรายวัน|Daily summary|每日汇总
ดูสถิติ / รีเฟรช|View statistics / refresh|查看统计／刷新
เริ่ม YYYY-MM-DD|Start YYYY-MM-DD|开始日期 YYYY-MM-DD
สิ้นสุด YYYY-MM-DD|End YYYY-MM-DD|结束日期 YYYY-MM-DD
มูลค่าธุรกรรม|Transaction value|交易金额
รายการที่ไม่ทราบมูลค่า THB · สกุลเงินจัดอันดับตามมูลค่า THB ที่เกี่ยวข้อง|transactions without THB value. Currencies ranked by associated THB value.|笔交易无THB金额。币种按相关THB金额排名。
ยอดเป็นมูลค่าธุรกรรม ไม่ใช่กำไร · ไม่รวม|Transaction value, not profit · excluding|此为交易金额而非利润 · 不含
จำนวนรายการในช่วงวัน:|Transactions in date range:|日期范围内交易：
จำนวนรายการ|Transactions|交易笔数
รายการไม่ทราบมูลค่า THB|Unknown THB value|THB金额未知
มูลค่าเทียบ THB|Equivalent THB value|THB等值金额
มูลค่า THB|THB value|THB金额
ร้านรับ (หน่วย)|Store receives (units)|店铺收取（单位）
ร้านจ่าย (หน่วย)|Store pays (units)|店铺支付（单位）
สรุปยอด|Totals by period|期间汇总
รายเดือน|Monthly|按月
รายวัน|Daily|按日
รายปี|Yearly|按年
วันที่ทำรายการ|Transaction date|交易日期
วันที่|Date|日期
เดือน|Month|月份
ปี|Year|年份
สรุป|Summary|汇总
อันดับ|Rank|排名
ผู้ใช้|User|用户
ลูกค้า|Customer|客户
เลขรายการ|Transaction number|交易编号
ประเภท|Type|类型
สกุลเงิน|Currency|币种
สถานะ|Status|状态
สิทธิ์|Role|权限
หมายเหตุ|Note|备注
จำนวน|Amount|金额
อัตรา|Rate|汇率
ชื่อ|Name|名称
จาก|From|从
เป็น|To|到
บันทึก|Save|保存
ไม่มีรายการ|No transactions|暂无交易
เฉพาะ admin|Admins only|仅限管理员
กรุณาเลือกรายการ|Select a transaction|请选择交易
กรุณาเลือกบัญชี|Select an account|请选择账户
กรุณาเลือกข่าว|Select news|请选择新闻
กรุณาเลือกภาพข่าว|Choose a news image|请选择新闻图片
ออฟไลน์|Offline|离线
ไม่สำเร็จ|Failed|失败
เก่าเกิน|Outdated|已过期
กำลังเตรียมข้อมูลให้คุณ…|Preparing your details…|正在准备您的信息…
US Dollar|US Dollar|美元
Euro|Euro|欧元
British Pound|British Pound|英镑
Japanese Yen|Japanese Yen|日元
Chinese Yuan|Chinese Yuan|人民币
South Korean Won|South Korean Won|韩元
Singapore Dollar|Singapore Dollar|新加坡元
Australian Dollar|Australian Dollar|澳元
Canadian Dollar|Canadian Dollar|加元
Thai Baht|Thai Baht|泰铢
Language|Language|语言
ภาษา|Language|语言
บัญชีไม่พร้อมใช้งาน|Account unavailable|账户不可用
ข้อมูลผู้ใช้|User details|用户信息
สกุลเงินไม่ถูกต้อง|Invalid currency|币种不正确
จำนวนเงินไม่ถูกต้อง|Invalid amount|金额不正确
กรุณาตรวจสอบจำนวนเงิน|Check the amount|请检查金额
รหัสผ่านเดิมไม่ถูกต้อง|Current password is incorrect|当前密码不正确
รหัสผ่านปัจจุบันไม่ถูกต้อง|Current password is incorrect|当前密码不正确
อีเมลไม่ถูกต้อง|Invalid email|邮箱格式不正确
เบอร์โทรไม่ถูกต้อง|Invalid phone number|电话号码不正确
ไม่พบข่าวนี้|News not found|未找到新闻
ลิงก์ข่าวต้องเป็น http:// หรือ https:// ที่ถูกต้อง และไม่มีข้อมูลเข้าสู่ระบบ|Article URL must be valid http:// or https:// without login credentials|新闻链接必须是有效的http://或https://，且不包含登录信息
ก่อนส่งใบเสร็จ|before sending the receipt|发送收据前
และตรวจชื่อผู้รับก่อนโอน|and check the recipient before transferring|并在转账前核对收款人
รายการ|transactions|笔交易
ชำระ|Pay|支付
ตรวจสอบยอดและการรับชำระหรือส่งมอบเงินจริงกับร้านแล้วใช่หรือไม่?|Have you verified the amount and actual payment or currency handover with the store?|是否已与店铺核实金额及实际付款或货币交付？
การอนุมัตินี้ไม่ได้เชื่อมต่อธนาคาร|This approval does not connect to a bank|此审批未与银行连接
นำเงินต่างประเทศตามยอดข้างต้นมาส่งมอบที่ร้าน|Bring the stated foreign currency amount to the store|请将上述金额的外币带到店铺交付
เจ้าหน้าที่ตรวจสอบเงินและอัตราก่อนอนุมัติ ไม่ต้องโอนบาทซ้ำ|Staff will check cash and rates before approval. Do not transfer THB again.|工作人员会核实货币及汇率后批准，无需再次转账泰铢。
ร้านยังไม่ได้เชื่อมผู้ให้บริการรับบัตร|The store has not connected a card payment provider|店铺尚未连接银行卡付款服务商
เมื่อเปิดบริการ จะชำระยอด THB บนหน้าผู้ให้บริการ|When available, pay the THB amount on the provider page|开通后将在服务商页面支付THB金额
EXORA ไม่เก็บเลขบัตร วันหมดอายุ หรือ CVV|EXORA does not store card numbers, expiry dates or CVV|EXORA不保存卡号、有效期或CVV
ส่งรหัสยืนยันไปยังอีเมลที่ลงทะเบียนไว้|Send a verification code to your registered email|向注册邮箱发送验证码
OTP 6 หลัก ใช้ได้ 10 นาที และใช้ได้ครั้งเดียว|6-digit OTP, valid for 10 minutes, single use|6位验证码，有效期10分钟，仅可使用一次
ราคาซื้อ–ขายของร้านจะเปลี่ยนตามข้อมูลออนไลน์และส่วนต่างที่กำหนด|Store rates will follow online data and the configured spread|店铺汇率将根据在线数据及设定价差变化
ยืนยันเปิดใช้ราคาซื้อ–ขายอัตโนมัติ?|Enable automatic buy / sell pricing?|确认启用自动买入／卖出定价？
ตั้ง EXORA_GMAIL_APP_PASSWORD ของ|Set EXORA_GMAIL_APP_PASSWORD for|请设置此账户的EXORA_GMAIL_APP_PASSWORD：
ออนไลน์|Online|在线
ราคาซื้อ–ขายอัตโนมัติ|Automatic buy / sell rates|自动买入／卖出价
ราคาซื้อ–ขายที่ร้านตั้ง|Store-set buy / sell rates|店铺设定买入／卖出价
ข้อมูล|Data|数据
ตรวจสอบ|Check|检查
ภาษาไม่ถูกต้อง|Invalid language|语言不正确
เตรียมเงินสำหรับทุกการเดินทาง|Currency for every journey|为每次旅程准备货币
แลกเงิน ติดตามรายการ และรับใบเสร็จในโปรแกรมเดียว|Exchange currency, track transactions and receive receipts in one app|在同一应用中兑换货币、跟踪交易并获取收据
เตรียมพร้อมสำหรับทุกการเดินทาง|Ready for every journey|为每次旅程做好准备
กำลัง|In progress|正在进行
รูปภาพ|Image|图片
เลือกหลักฐาน|Choose proof|选择凭证
ตรวจสอบชื่อผู้รับและยอดเงินก่อนโอน แนบหลักฐานเพื่อให้เจ้าหน้าที่ตรวจสอบ|Check the recipient and amount before transfer. Attach proof for staff review.|转账前请核对收款人及金额，并上传凭证供工作人员审核。
สี|Color|颜色
เริ่ม|Start|开始
สิ้นสุด|End|结束
active|Active|正常
inactive|Inactive|停用
banned|Banned|已封禁
deleted|Deleted|已删除
admin|Admin|管理员
staff|Staff|工作人员
user|Customer|客户
BUY|Buy|买入
SELL|Sell|卖出
SWAP|Swap|兑换
'''
DATA+='''
โอนบัญชีธนาคาร|Bank account settlement|银行账户结算
รายการโอนบัญชีธนาคาร|Bank settlement orders|银行结算订单
บัญชีรับเงินของลูกค้า|Customer receiving account|客户收款账户
ร้านตรวจข้อมูลและยืนยันช่องทางธนาคารก่อนเปิดให้ชำระเงิน|Staff verify details and bank route before payment|工作人员核实资料及银行渠道后方可付款
ชื่อบัญชีผู้รับเงิน|Beneficiary name|收款人姓名
ธนาคารผู้รับ / SWIFT|Receiving bank / SWIFT|收款银行／SWIFT
เลขบัญชีผู้รับ / IBAN|Receiving account / IBAN|收款账号／IBAN
ประเทศปลายทาง|Destination country|收款国家
จาก THB เป็นสกุลเงิน|From THB to currency|从THB兑换至
ส่งข้อมูลให้เจ้าหน้าที่ตรวจ|Submit details for review|提交资料审核
ธนาคารดำเนินการรับ–โอนเงินจริงภายนอกโปรแกรม เจ้าหน้าที่บันทึกผลใน EXORA|Bank operations take place outside EXORA; staff record results here|银行在程序外执行真实收付款，工作人员在此记录结果
สร้างรายการ|Create order|创建订单
รอตรวจข้อมูลผู้รับ|Recipient review pending|待审核收款资料
ตรวจข้อมูลแล้ว / รอรับราคา|Details verified / awaiting quote|资料已核实／待报价
รอโอนชำระ|Awaiting bank payment|等待转账付款
รอตรวจเงินเข้า|Awaiting incoming funds review|待核实到账
รับชำระแล้ว / รอโอนจ่าย|Payment verified / awaiting payout|收款已确认／待支付
กำลังดำเนินการโอนจ่าย|Payout in progress|正在支付
โอนจ่ายสำเร็จ|Payout recorded complete|支付已记录完成
ไม่ผ่านการตรวจข้อมูล|Details rejected|资料审核未通过
ผลตรวจตัวตนโดยเจ้าหน้าที่ / อ้างอิงการตรวจ|Staff identity check / verification reference|工作人员身份审核／核查参考
ยืนยันธนาคารรองรับประเทศ สกุลเงิน บัญชี และยอดรับสุทธิรวมค่าธรรมเนียม|Confirm bank route, account, currency and net payout including fees|确认银行渠道、账户、币种及含手续费后的净到账金额
บันทึกหลังตรวจจริงภายนอกระบบเท่านั้น ไม่ใช่ eKYC อัตโนมัติ|Record only after an external check; not automated eKYC|仅在程序外完成实际核查后记录，并非自动eKYC
ยืนยันผลตรวจและช่องทางธนาคาร|Confirm checks and bank route|确认审核与银行渠道
ปฏิเสธข้อมูลผู้รับ|Reject recipient details|拒绝收款资料
เลขอ้างอิงเงินเข้าที่ตรวจจากธนาคาร|Incoming bank reference verified by staff|经工作人员核实的银行收款参考号
ยืนยันรับเงินจริงเข้าบัญชีร้าน|Confirm actual funds received|确认店铺账户实际到账
เริ่มดำเนินการโอนจ่าย|Start payout processing|开始处理支付
เลขอ้างอิงการโอนจ่ายจากธนาคาร|Bank payout reference|银行支付参考号
หลักฐานการโอนจ่าย|Payout proof|支付凭证
ยืนยันว่าตรวจผลโอนสำเร็จจากธนาคารแล้ว?|Confirm you checked successful transfer with the bank?|确认已向银行核实转账成功？
บันทึกผลโอนสำเร็จและส่งใบเสร็จ|Record completed payout and email receipt|记录支付完成并发送收据
เลขอ้างอิงการโอนจ่าย:|Payout reference:|支付参考号：
เลขอ้างอิงการชำระ|Payment reference|付款参考号
กรุณาตรวจรายการผ่านขั้นตอนโอนบัญชีธนาคาร|Review this order through bank settlement|请通过银行结算流程审核此订单
ดูรายละเอียด|View details|查看详情
จำลองแลกเงินออนไลน์|Online exchange simulation|在线兑换模拟
จำลองออนไลน์|Online simulation|在线模拟
SIMULATION · ไม่โอนเงินจริง ไม่ยืนยันตัวตนจริง ไม่ส่งอีเมลจริง|SIMULATION · No real transfers, identity checks or emails|模拟模式 · 不真实转账、不真实验证身份、不发送邮件
บัญชีออมทรัพย์ร้านจำลอง: DEMO-STORE-0001|Demo store savings account: DEMO-STORE-0001|店铺模拟储蓄账户：DEMO-STORE-0001
บัญชีรับเงิน → ตรวจตัวตน → รับราคา → ชำระจำลอง → ตรวจรับชำระ → โอนจ่ายจำลอง → ใบเสร็จ|Recipient account → Identity check → Quote → Demo payment → Review → Demo payout → Receipt|收款账户 → 身份审核 → 报价 → 模拟付款 → 审核 → 模拟支付 → 收据
ใช้ข้อมูลสมมติและบัญชี DEMO- เท่านั้น|Use fictional details and DEMO- accounts only|仅使用虚构资料及DEMO-账号
ชื่อผู้รับจำลอง|Demo recipient name|模拟收款人姓名
ธนาคารจำลอง|Demo bank|模拟银行
เลขบัญชีจำลอง|Demo account number|模拟账号
ประเทศปลายทางจำลอง|Demo destination country|模拟收款国家
ส่งตรวจตัวตนจำลอง|Submit demo identity review|提交模拟身份审核
SIMULATION · ไม่มีการเคลื่อนย้ายเงินจริง|SIMULATION · No real money movement|模拟模式 · 无真实资金流动
รับราคา / คำนวณใหม่|Get quote / recalculate|获取报价／重新计算
ยืนยันชำระเงินจำลอง|Submit demo payment|确认模拟付款
ยืนยันตัวตนจำลอง|Approve demo identity|通过模拟身份审核
ยืนยันรับชำระจำลอง|Confirm demo payment|确认模拟收款
เริ่มโอนจ่ายจำลอง|Start demo payout|开始模拟支付
ยืนยันโอนสำเร็จจำลอง|Complete demo payout|确认模拟支付完成
ปฏิเสธจำลอง|Reject demo request|拒绝模拟申请
ไม่ได้ส่งอีเมลจริง|No email was sent|未发送真实邮件
บันทึก PDF จำลอง|Save demo PDF|保存模拟PDF
สร้างรายการจำลอง|Create demo request|创建模拟申请
ดูรายละเอียด / รีเฟรช|Details / refresh|详情／刷新
รีเฟรช|Refresh|刷新
รอตรวจตัวตนจำลอง|Demo identity review pending|待模拟身份审核
ผ่านตรวจตัวตนจำลอง|Demo identity approved|模拟身份已通过
รอชำระจำลอง|Awaiting demo payment|待模拟付款
รอตรวจรับชำระจำลอง|Demo payment review pending|待模拟收款审核
รับชำระจำลองแล้ว|Demo payment verified|模拟付款已确认
กำลังโอนจ่ายจำลอง|Demo payout in progress|正在模拟支付
สำเร็จจำลอง|Demo completed|模拟完成
ใช้เลขบัญชีจำลองที่ขึ้นต้น DEMO- เท่านั้น|Use a demo account beginning DEMO- only|仅使用以DEMO-开头的模拟账号
ให้แอดมินอีกบัญชีตรวจรายการนี้|Another admin must review this request|请由其他管理员审核此申请
รายการยังไม่สำเร็จจำลอง|Demo request is not completed yet|模拟申请尚未完成
ราคารับซื้อของร้าน · THB ต่อ 1 หน่วย|Store buy rates · THB per 1 unit|店铺买入价 · 每单位泰铢价格
ไม่มีรายการรอตรวจ|No pending reviews|暂无待审核交易
อีเมลแจ้งเตือนค้าง:|Email alerts pending:|待发送提醒邮件：
ส่งซ้ำ|Retry|重试
อนุมัติแล้ว แต่ส่งอีเมลไม่สำเร็จ:|Approved, but email delivery failed:|交易已批准，但邮件发送失败：
กดส่งใบเสร็จอีกครั้งได้ในรายละเอียด|Retry sending the receipt from transaction details|可在交易详情中重新发送收据
แลกเงินอย่างมั่นใจ พร้อมออกเดินทางไปทุกจุดหมาย|Exchange with confidence. Ready for every destination.|安心兑换，准备前往每个目的地。
ข้อมูลเพิ่มเติม|Additional information|补充信息
ลิงก์แผนที่|Map link|地图链接
อีเมลติดต่อ|Contact email|联系邮箱
เว็บไซต์|Website|网站
ข้อมูลแต่ละช่องต้องไม่เกิน 500 ตัวอักษร|Each field must be at most 500 characters|每个字段最多500个字符
ลิงก์ต้องเป็น http:// หรือ https:// ที่ถูกต้อง|Enter a valid http:// or https:// URL|请输入有效的http://或https://链接
อีเมลติดต่อไม่ถูกต้อง|Invalid contact email|联系邮箱格式不正确
OTP ไม่ถูกต้อง กรุณาตรวจสอบรหัส (ลองได้ไม่เกิน 5 ครั้ง)|Invalid OTP. Check the code (maximum 5 attempts).|验证码错误，请检查（最多尝试5次）。
OTP ไม่ถูกต้อง หมดอายุ หรือใช้ไปแล้ว กรุณาขอรหัสใหม่|OTP invalid, expired or already used. Request a new code.|验证码无效、已过期或已使用，请重新获取。
OTP ไม่สามารถใช้กับบัญชีนี้ได้ กรุณาขอรหัสใหม่|OTP is not valid for this account. Request a new code.|此验证码不适用于该账户，请重新获取。
กรุณากรอกอีเมลที่ลงทะเบียนให้ถูกต้อง|Enter your registered email correctly|请正确输入注册邮箱
กรุณาใช้รหัสผ่านใหม่ที่ไม่ใช่รหัสเริ่มต้น|Choose a password different from the default|请选择非默认密码
ขอ OTP บ่อยเกินไป กรุณารออย่างน้อย 1 นาที (สูงสุด 5 ครั้งต่อชั่วโมง)|Too many OTP requests. Wait at least 1 minute (maximum 5 per hour).|请求验证码过于频繁，请至少等待1分钟（每小时最多5次）。
รหัสผ่านใหม่ต้องมี 8–256 ตัวอักษร|New password must have 8–256 characters|新密码须包含8至256个字符
หากอีเมลนี้ลงทะเบียนและบัญชีพร้อมใช้งาน ระบบจะส่ง OTP ให้ กรุณาตรวจกล่องจดหมายและสแปม|If this email is registered to an active account, an OTP will be sent. Check your inbox and spam folder.|若此邮箱属于有效账户，系统将发送验证码。请检查收件箱和垃圾邮件。
ก่อนส่ง OTP|before sending an OTP|发送验证码前
กรุณากรอกจำนวนเงินที่โอนเป็นบาท|Enter the transfer amount in THB|请输入泰铢转账金额
จำนวนเงินที่โอนต้องมากกว่า 0|Transfer amount must be positive|转账金额须大于0
จำนวนเงินที่โอนน้อยเกินไป|Transfer amount is too small|转账金额过小
จำนวนเงินและอัตราไม่ถูกต้อง|Invalid amount or rate|金额或汇率不正确
ชื่อลูกค้าต้องมี 1–80 ตัวอักษร|Customer name must have 1–80 characters|客户姓名须包含1至80个字符
ช่องทางนี้สำหรับส่งมอบเงินต่างประเทศที่ร้าน|This method is for in-store foreign currency handover|此方式用于到店交付外币
ช่องทางบัตรยังไม่เปิดบริการ ต้องตั้งผู้ให้บริการก่อน|Card payment is unavailable. Configure a provider first.|银行卡付款尚未开通，请先配置服务商。
กรุณาเลือกวิธีชำระเงินที่เปิดบริการ|Choose an available payment method|请选择可用的付款方式
ธนาคารผู้โอน|Sender bank|转出银行
ภาพสลิปไม่ถูกต้องหรือใหญ่เกินกำหนด|Invalid or oversized payment image|付款凭证图片无效或过大
มูลค่าเงินบาทไม่ถูกต้อง|Invalid THB value|THB金额不正确
ยอดโอนต้องตรงกับยอด THB ของรายการ|Transfer amount must match the transaction THB total|转账金额须与交易的THB总额一致
รองรับสลิป JPG/PNG ไม่เกิน 10 MB|JPG/PNG payment proof up to 10 MB|支持JPG／PNG付款凭证，不超过10MB
รองรับ JPG/PNG ไม่เกิน 10 MB|JPG/PNG images up to 10 MB|支持JPG／PNG图片，不超过10MB
รายการนี้ได้รับการตรวจสอบแล้ว|This transaction has already been reviewed|此交易已审核
รายการนี้ไม่มีสลิป|No payment proof for this transaction|此交易没有付款凭证
รูปแบบไฟล์ไม่ถูกต้อง|Invalid file format|文件格式不正确
วันเวลาที่โอน|Transfer date and time|转账日期与时间
วันเวลาโอนใช้รูปแบบ YYYY-MM-DD HH:MM|Use YYYY-MM-DD HH:MM for transfer time|转账时间格式为YYYY-MM-DD HH:MM
สถานะไม่ถูกต้อง|Invalid status|状态不正确
หมายเหตุต้องไม่เกิน 500 ตัวอักษร|Note must be at most 500 characters|备注最多500个字符
เฉพาะ admin สามารถตรวจสอบสลิปได้|Only admins can review payment proof|仅管理员可审核付款凭证
เฉพาะเจ้าของรายการ|Transaction owner only|仅限交易所有者
เลขบัญชีผู้โอนต้องมี 6–20 หลัก|Sender account number must have 6–20 digits|付款账号须为6至20位数字
เลขอ้างอิงยาวเกินไป|Reference number is too long|参考编号过长
แนบใหม่ได้เฉพาะรายการปฏิเสธ|Proof can be replaced only for rejected transactions|仅已拒绝交易可更换凭证
แอดมินไม่สามารถอนุมัติหรือปฏิเสธรายการของตัวเอง|Admins cannot approve or reject their own transactions|管理员不能批准或拒绝自己的交易
ให้ admin ตั้งค่าบัญชีธนาคารรับเงินของร้านก่อนใช้งานวิธีนี้|An admin must configure the store receiving account first|请管理员先设置店铺收款账户
ไฟล์ภาพไม่ถูกต้อง|Invalid image file|图片文件不正确
ไม่พบรายการ|Transaction not found|未找到交易
ไม่พบไฟล์สลิป|Payment proof file not found|未找到付款凭证文件
ไม่มีสิทธิ์ดูรายการนี้|You cannot view this transaction|您无权查看此交易
กรอกธนาคาร ชื่อบัญชี และเลขบัญชีร้านให้ครบ หรือเว้นว่างทั้งสามช่อง|Fill all receiving bank details or leave all three fields empty|请完整填写银行、账户姓名及账号，或将三项全部留空
กรุณาตรวจสอบชื่อ เบอร์โทร และข้อความแนะนำ|Check name, phone and profile text|请检查姓名、电话及资料文字
กรุณาตรวจสอบชื่อและรหัสสกุลเงิน|Check currency name and code|请检查币种名称及代码
กรุณาระบุชื่อร้าน|Enter the store name|请输入店铺名称
ข้อความยาวเกินไป|Text is too long|文字过长
รองรับ JPG/PNG ไม่เกิน 25 ล้านพิกเซล|JPG/PNG images up to 25 million pixels|支持JPG／PNG图片，最多2500万像素
รูปต้องไม่เกิน 10 MB|Image must be at most 10 MB|图片不得超过10MB
สิทธิ์หรือสถานะไม่ถูกต้อง|Invalid role or status|权限或状态不正确
สีไม่ถูกต้อง|Invalid color|颜色不正确
อัตราต้องมากกว่า 0 และราคาขายไม่น้อยกว่ารับซื้อ|Rates must be positive; sell rate must not be below buy rate|汇率须大于0，卖出价不得低于买入价
อีเมลนี้ถูกใช้แล้ว|Email already in use|此邮箱已被使用
เลขบัญชีร้านไม่ถูกต้อง|Invalid store account number|店铺账号不正确
ไม่พบบัญชีที่จัดการได้|No manageable account found|未找到可管理账户
ไม่สามารถปิดสิทธิ์ admin ของตัวเอง|You cannot remove your own admin access|不能移除自己的管理员权限
ไม่สามารถลบบัญชีตัวเอง|You cannot delete your own account|不能删除自己的账户
Password ต้องมีอย่างน้อย 8 ตัวอักษร|Password must have at least 8 characters|密码至少8个字符
Username ต้องมีอย่างน้อย 3 ตัวอักษร|Username must have at least 3 characters|用户名至少3个字符
Username หรือ Email นี้ถูกใช้งานแล้ว|Username or email is already in use|此用户名或邮箱已被使用
กรุณากรอกข้อมูลให้ครบทุกช่อง|Fill in all required fields|请填写所有必填字段
กรุณากรอกเบอร์โทรที่ถูกต้อง|Enter a valid phone number|请输入有效电话号码
กรุณาใช้ลืมรหัสผ่านและยืนยัน OTP ทางอีเมลก่อนตั้งรหัสผ่านใหม่|Use forgot password and verify email OTP before resetting|重置密码前请使用忘记密码并验证邮箱验证码
ชื่อผู้ใช้ต้องไม่เกิน 80 ตัวอักษร และไม่มี @ หรือช่องว่าง|Username must be at most 80 characters, without @ or spaces|用户名最多80个字符，不含@或空格
ชื่อผู้ใช้หรืออีเมลนี้ถูกใช้งานแล้ว|Username or email is already in use|此用户名或邮箱已被使用
รูปแบบ Email ไม่ถูกต้อง|Invalid email format|邮箱格式不正确
สร้างบัญชีสำเร็จ สามารถเข้าสู่ระบบได้แล้ว|Account created. You can now sign in.|账户创建成功，现在可以登录。
อีเมลยาวเกินไป|Email is too long|邮箱地址过长
กรุณาคำนวณใบเสนอราคาใหม่ก่อนส่งรายการ|Calculate a new quote before submitting|提交前请重新计算报价
กรุณาเลือกสกุลเงินต่างกัน|Choose two different currencies|请选择两个不同币种
จำนวนเงินต้องอยู่ระหว่าง 0 ถึง 1,000,000,000|Amount must be greater than 0 and at most 1,000,000,000|金额须大于0且不超过1,000,000,000
จำนวนเงินน้อยเกินไป|Amount is too small|金额过小
จำนวนเงินยาวเกินไป|Amount input is too long|金额输入过长
มูลค่ารายการเกินขอบเขตที่ระบบรองรับ|Transaction value exceeds the supported limit|交易金额超过系统支持范围
ยอดหรือข้อมูลใบเสนอราคาถูกเปลี่ยน กรุณาคำนวณใหม่|Quote amount or details changed. Recalculate.|报价金额或信息已更改，请重新计算。
ยอดเงินหรืออัตราเกินขอบเขตที่ระบบรองรับ|Amount or rate exceeds the supported limit|金额或汇率超过系统支持范围
ร้านยังไม่ได้ตั้งอัตราสำหรับสกุลเงินนี้|The store has not set a rate for this currency|店铺尚未设置此币种汇率
เลขอ้างอิงการโอนนี้ถูกใช้ในรายการอื่นแล้ว|This transfer reference was used in another transaction|此转账参考编号已用于其他交易
ใบเสนอราคานี้ถูกใช้แล้ว กรุณาสร้างรายการใหม่|This quote was already used. Create a new transaction.|此报价已使用，请创建新交易。
ใบเสนอราคาหมดอายุ กรุณาคำนวณใหม่|Quote expired. Recalculate.|报价已过期，请重新计算。
ใบเสนอราคาเป็นของบัญชีอื่น|Quote belongs to another account|报价属于其他账户
ไม่พบสกุลเงิน|Currency not found|未找到币种
กรุณากรอก|Please enter|请输入
ก่อน|before|之前
pending|Pending review|待审核
approved|Approved|已批准
rejected|Rejected|已拒绝
legacy|Legacy|历史记录
'''
CATALOG={}
for line in DATA.strip().splitlines():
    if not line.strip():continue
    source,english,chinese=line.split('|');CATALOG[source]=(english,chinese)
