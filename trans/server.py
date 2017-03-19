from flask import request, Flask, render_template, session, redirect, url_for, escape
from flask import send_from_directory, abort, send_file, make_response
from werkzeug import secure_filename
import json
import os
import trans
import io

UPLOAD_FOLDER = 'temp/'
ALLOWED_EXTENSIONS = set(['lang', 'py'])

app = Flask(__name__)
app.secret_key = '123456'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 上传文件限制

GRES = {}

users = {
    'admin@a': 'admin',
    'coc@c': 'admin',
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def _yz_user(ses):
    if 'email' in ses and 'password' in ses:
        if ses['email'] in users and ses['password'] == users[ses['email']]:
            return True

    return False


@app.route('/')
@app.route('/index')
def index():
    if not _yz_user(session):
        return redirect(url_for('login'))
    else:
        return render_template('trans.html', name="0")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if _yz_user(session):
            return redirect(url_for('index'))
        return render_template("login.html")
    else:
        session['email'] = request.form['email']
        session['password'] = request.form['password']
        if _yz_user(session):
            if not os.path.isdir(UPLOAD_FOLDER + session['email']):
                os.mkdir(UPLOAD_FOLDER + session['email'])

            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('password', None)
    return redirect(url_for('index'))


@app.route('/save', methods=["POST"])
def save():
    data = json.loads(request.form['data'])
    GRES[session['email']]['edit'] = data
    return "ok"


# @app.route('/FileUpload/Upload', methods=['POST'])
# def Upload(**args):
#     file = request.files['file_data']
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(UPLOAD_FOLDER, session['email'] + "/" + filename))
#     return json.dumps({"errno": 0, "errmsg": "上传成功"})

@app.route('/upload', methods=['POST'])
def upload():
    source = json.loads(request.form['data'])

    sdata = trans.load(source)
    res = trans.parse(sdata)

    GRES[session['email']] = {}
    GRES[session['email']]['source'] = source
    GRES[session['email']]['sdata'] = sdata

    return json.dumps(res)


@app.route('/download')
def download():
    email = session['email']
    tmp = {}
    if email in GRES:
        if 'zh_CN' in GRES[email]['sdata']:
            tmp = GRES[email]['sdata']['zh_CN']
        if 'edit' in GRES[email]:
            for key in GRES[email]['edit']:
                tmp[key] = GRES[email]['edit'][key]
    if not tmp:
        return "无数据可下载"

    text = ""
    for key in tmp:
        text += key + "=" + tmp[key] + "\n"

    # text = 'itemgroup.fcombat=古代装备\nitemgroup.fblocks=古代方块\nitemgroup.ffood=古代食物\nitemgroup.fitems=古代物品\nitemgroup.fmaterial=古代材料\nitemgroup.ftools=古代工具\nitemgroup.ffigurines=雕像收集\nitemgroup.fbones=恐龙骨头\nbiome.anu.name=黑暗之地\nachievement.firstfossil=挖出骨头!\nachievement.firstfossil.desc=开采一块化石或永久冻土.\nachievement.analyzer=更多化石!\nachievement.analyzer.desc=合成一台分析仪.\nachievement.tablet=古代预言\nachievement.tablet.desc=在分析遗迹碎片时获得一块石版画.\nachievement.dinodna=Bingo!恐龙DNA!\nachievement.dinodna.desc=在分析活体化石时获得任意一种DNA.\nachievement.cultivate=古典培养学!\nachievement.cultivate.desc=合成一台培养槽.\nachievement.dinoegg=它是什么品种的?\nachievement.dinoegg.desc=培养出一枚恐龙蛋.\nachievement.mammalembryo=哎哟!\nachievement.mammalembryo.desc=培养出哺乳动物的胚胎.\nachievement.birdegg=叽叽喳喳!\nachievement.birdegg.desc=培养出一枚鸟蛋.\nachievement.sifter=肮脏的工作!\nachievement.sifter.desc=合成一个筛子.\nachievement.fossilseeds=来自过去的植物!\nachievement.fossilseeds.desc=在分析植物化石时获得任何一种化石种子.\nachievement.failuresaurus=巨大的失误!\nachievement.failuresaurus.desc=不小心从培养槽中培养出畸龙.\nachievement.failuresaurusanalyzer=计划重启!\nachievement.failuresaurusanalyzer.desc=从畸龙肉中得到任意一种DNA.\nachievement.findanutotem=这是啥?\nachievement.findanutotem.desc=找到一个神秘塑像.\nachievement.anuportal=中世纪?\nachievement.anuportal.desc=启动神秘塑像.\nachievement.anubiteencounter=雕像活了!\nachievement.anubiteencounter.desc=遇到阿努.\nachievement.anuattack=亡灵统治者!\nachievement.anuattack.desc=召唤阿努.\nachievement.anudead=中世纪.\nachievement.anudead.desc=消灭阿努.\nachievement.arcworkbench=破房子!\nachievement.arcworkbench.desc=合成考古工作桌\nachievement.fixedsword=舞刀弄剑!\nachievement.fixedsword.desc=使用考古工作桌修复破损的古代剑.\nachievement.fixedhelmet=智慧之冠!\nachievement.fixedhelmet.desc=使用考古工作桌修复破损的古代头盔.\nachievement.fixedvase=精致的花瓶!\nachievement.fixedvase.desc=使用考古工作桌修复蜗壳,陶罐或者陶杯.\nachievement.dinopedia=恐龙百科!\nachievement.dinopedia.desc=合成一本用于查看恐龙生长状态的恐龙百科.\nachievement.scarab=终极宝石!\nachievement.scarab.desc=从化石方块中得到一个圣甲虫宝石.\nachievement.scarabtools=魔法工具!\nachievement.scarabtools.desc=合成任意一种圣甲虫工具.\nachievement.bluescarab=蓝色甲虫!\nachievement.bluescarab.desc=合成海蓝圣甲虫宝石.\nachievement.key=关键信息!\nachievement.key.desc=将古代时钟嵌入时间机器中.\nachievement.clock=时空回流!\nachievement.firstdino=为了拯救灭绝的危机!\nachievement.firstdino.desc=孵化你的第一个恐龙蛋.\nachievement.theking=暴君!\nachievement.theking.desc=抚养一头霸王龙.\nachievement.usurper=篡位者!\nachievement.usurper.desc=抚养一头脊龙.\nachievement.squire=这是... 大地主?\nachievement.squire.desc=抚养一头异特龙.\nachievement.intreasure=屋子?\nachievement.intreasure.desc=找到秘密的宝物房间.\nachievement.shear=One Big Sheep!\nachievement.shear.desc=Shear a Mammoth.\nenchantment.paleontology=古生物学\nenchantment.archeology=考古学\ntile.fossil.name=化石\ntile.skullblock.name=头骨\ntile.skulllantern.name=头骨灯笼\ntile.analyzer.name=分析仪\ntile.culturevat.name=培养槽\ntile.fossilworkbench.name=考古工作桌\ntile.fossil_drum.name=命令鼓\ntile.feederidle.name=喂食器\ntile.feederactive.name=喂食器\ntile.permafrost.name=永久冻土\ntile.icedstone.name=冰石\ntile.timemachine.name=时间机器\ntile.tar.name=焦油\ntile.palaeoraphelog.name=古树原木\ntile.palaeorapheleaves.name=古树树叶\ntile.palaeoraphesapling.name=古树树苗\ntile.palaeorapheplanks.name=古树木板\ntile.palaeorapheslab.palae.name=古树台阶\ntile.palaeorapheslabdouble.name=古树台阶\ntile.palaeoraphestairs.name=古树楼梯\ntile.volcanicash.name=火山灰\ntile.volcanicrock.name=火山岩\ntile.volcanicrockhot.name=炙热火山岩\ntile.sarracina.name=瓶子草\ntile.fernblock.name=古代蕨类\ntile.volcanicbrick.name=火山岩砖\ntile.amberore.name=琥珀矿石\ntile.ancientstone.name=古代石头\ntile.ancientstonebrick.name=古代石砖\ntile.ancientwood.name=古代木头\ntile.ancientwoodpillar.name=古代木头柱子\ntile.ancientglass.name=古代玻璃\ntile.ancientwoodplate.name=古代木板\ntile.ancientwoodstairs.name=古代木头楼梯\ntile.ancientstonestairs.name=古代石头楼梯\ntile.figurine.name=木质雕像\ntile.sifter.name=筛子\ntile.volcanicstairs.name=火山岩楼梯\ntile.volcanicslab.volcanicbrick.name=火山岩台阶\ntile.volcanicslabdouble.volcanicbrick.name=火山岩台阶\ntile.ancientwoodslab.ancientwood.name=古代木头台阶\ntile.ancientwooddoubleslab.ancientwood.name=古代木头台阶\ntile.ancientstoneslab.ancientstone.name=古代石头台阶\ntile.ancientstonedoubleslab.ancientstone.name=古代石头台阶\ntile.limestone.name=石灰石\ntile.limestonebrick.name=石灰石砖\ntile.dillhoffia.name=Dillhoffia\ntile.magnolia.name=木兰花\ntile.slimetrail.name=畸龙尾迹\ntile.obsidianspikes.name=黑曜石尖刺\ntile.ancientchest.name=古代宝物箱\ntile.home_portal.name=主世界传送门\ntile.sarcophagus.name=神秘石棺\ntile.strongglass.name=Reinforced Glass\ntile.anu_block.name=Anu Statue\ntile.anubitestatue.name=Anubite Statue\ntile.densesand.name=Dense Sand\ntile.figurine.figurine_steve_pristine.name=质朴史蒂夫雕像\ntile.figurine.figurine_skeleton_pristine.name=质朴骷髅雕像\ntile.figurine.figurine_zombie_pristine.name=质朴僵尸雕像\ntile.figurine.figurine_pigzombie_pristine.name=质朴末影人雕像\ntile.figurine.figurine_enderman_pristine.name=质朴僵尸猪人雕像\ntile.figurine.figurine_steve_damaged.name=破损史蒂夫雕像\ntile.figurine.figurine_skeleton_damaged.name=破损骷髅雕像\ntile.figurine.figurine_zombie_damaged.name=破损僵尸雕像\ntile.figurine.figurine_pigzombie_damaged.name=破损末影人雕像\ntile.figurine.figurine_enderman_damaged.name=破损僵尸猪人雕像\ntile.figurine.figurine_steve_broken.name=碎裂史蒂夫雕像\ntile.figurine.figurine_skeleton_broken.name=碎裂骷髅雕像\ntile.figurine.figurine_zombie_broken.name=碎裂僵尸雕像\ntile.figurine.figurine_pigzombie_broken.name=碎裂末影人雕像\ntile.figurine.figurine_enderman_broken.name=碎裂僵尸猪人雕像\ntile.figurine.figurine_mysterious.name=神秘雕像\ntile.vasevolute.damaged_volute.name=碎裂蜗壳\ntile.vasevolute.restored_volute.name=修复蜗壳\ntile.vasevolute.blackfigure_volute.name=黑纹蜗壳\ntile.vasevolute.redfigure_volute.name=红纹蜗壳\ntile.vasevolute.porcelain_volute.name=质朴蜗壳\ntile.vaseamphora.damaged_amphora.name=碎裂双耳陶罐\ntile.vaseamphora.restored_amphora.name=修复双耳陶罐\ntile.vaseamphora.blackfigure_amphora.name=黑纹双耳陶罐\ntile.vaseamphora.redfigure_amphora.name=红纹双耳陶罐\ntile.vaseamphora.porcelain_amphora.name=质朴双耳陶罐\ntile.vasekylix.damaged_kylix.name=碎裂基里克斯陶杯\ntile.vasekylix.restored_kylix.name=修复基里克斯陶杯\ntile.vasekylix.blackfigure_kylix.name=黑纹基里克斯陶杯\ntile.vasekylix.redfigure_kylix.name=红纹基里克斯陶杯\ntile.vasekylix.porcelain_kylix.name=质朴基里克斯陶杯\nitem.biofossil.name=活体化石\nitem.relicscrap.name=遗跡碎片\nitem.stonetablet.name=石版画\nitem.brokenancientsword.name=破损的古代剑\nitem.ancientsword.name=古代剑\nitem.brokenancienthelmet.name=破损的古代头盔\nitem.ancienthelmet.name=古代头盔\nitem.skullstick.name=头骨棒\nitem.scarabgem.name=圣甲虫宝石\nitem.scarabaxe.name=圣宝石斧\nitem.scarabpickaxe.name=圣宝石镐\nitem.scarabsword.name=圣宝石剑\nitem.scarabhoe.name=圣宝石锄\nitem.scarabshovel.name=圣宝石铲\nitem.dinopedia.name=恐龙百科\nitem.tooth.name=霸王龙牙\nitem.dagger.name=龙牙匕首\nitem.rawchickensoup.name=生鸡肉糜\nitem.cookedchickensoup.name=鸡汤\nitem.essenceofchicken.name=鸡精\nitem.emptyshell.name=空贝壳\nitem.sjl.name=烧酒螺\nitem.icedmeat.name=冰冻肉\nitem.woodjavelin.name=木制标枪\nitem.stonejavelin.name=石制标枪\nitem.ironjavelin.name=铁制标枪\nitem.goldjavelin.name=黄金标枪\nitem.diamondjavelin.name=钻石标枪\nitem.ancientjavelin.name=古代标枪\nitem.whip.name=鞭子\nitem.magicconch.name=神奇海螺\nitem.legbone.triceratops.name=三角龙腿骨\nitem.legbone.velociraptor.name=迅猛龙腿骨\nitem.legbone.trex.name=霸王龙腿骨\nitem.legbone.pterosaur.name=翼龙腿骨\nitem.legbone.plesiosaur.name=蛇颈龙腿骨\nitem.legbone.mosasaurus.name=沧龙腿骨\nitem.legbone.liopleurodon.name=滑齿龙腿骨\nitem.legbone.stegosaurus.name=剑龙腿骨\nitem.legbone.dilophosaurus.name=双脊龙腿骨\nitem.legbone.brachiosaurus.name=腕龙腿骨\nitem.legbone.spinosaurus.name=脊龙腿骨\nitem.legbone.compsognathus.name=美颌龙腿骨\nitem.legbone.ankylosaurus.name=背甲龙腿骨\nitem.legbone.pachycephalosaurus.name=肿头龙腿骨\nitem.legbone.deinonychus.name=恐爪龙腿骨\nitem.legbone.gallimimus.name=似鸡龙腿骨\nitem.legbone.allosaurus.name=异特龙腿骨\nitem.legbone.sarcosuchus.name=帝王鳄腿骨\nitem.legbone.ceratosaurus.name=角鼻龙腿骨\nitem.armbone.triceratops.name=三角龙臂骨\nitem.armbone.velociraptor.name=迅猛龙臂骨\nitem.armbone.trex.name=霸王龙臂骨\nitem.armbone.pterosaur.name=翼龙臂骨\nitem.armbone.plesiosaur.name=蛇颈龙臂骨\nitem.armbone.mosasaurus.name=沧龙臂骨\nitem.armbone.liopleurodon.name=滑齿龙臂骨\nitem.armbone.stegosaurus.name=剑龙臂骨\nitem.armbone.dilophosaurus.name=双脊龙臂骨\nitem.armbone.brachiosaurus.name=腕龙臂骨\nitem.armbone.spinosaurus.name=脊龙臂骨\nitem.armbone.compsognathus.name=美颌龙臂骨\nitem.armbone.ankylosaurus.name=背甲龙臂骨\nitem.armbone.pachycephalosaurus.name=肿头龙臂骨\nitem.armbone.deinonychus.name=恐爪龙臂骨\nitem.armbone.gallimimus.name=似鸡龙臂骨\nitem.armbone.allosaurus.name=异特龙臂骨\nitem.armbone.sarcosuchus.name=帝王鳄臂骨\nitem.armbone.ceratosaurus.name=角鼻龙臂骨\nitem.claw.triceratops.name=三角龙角\nitem.claw.velociraptor.name=迅猛龙爪\nitem.claw.trex.name=霸王龙牙\nitem.claw.pterosaur.name=翼龙指头\nitem.claw.plesiosaur.name=蛇颈龙牙\nitem.claw.mosasaurus.name=沧龙牙\nitem.claw.liopleurodon.name=滑齿龙胃须\nitem.claw.stegosaurus.name=剑龙背刺\nitem.claw.dilophosaurus.name=双脊龙爪\nitem.claw.brachiosaurus.name=腕龙爪\nitem.claw.spinosaurus.name=脊龙帆\nitem.claw.compsognathus.name=美颌龙爪\nitem.claw.ankylosaurus.name=背甲龙尾锤\nitem.claw.pachycephalosaurus.name=肿头龙头骨角\nitem.claw.deinonychus.name=恐爪龙爪\nitem.claw.gallimimus.name=似鸡龙爪\nitem.claw.allosaurus.name=异特龙爪\nitem.claw.sarcosuchus.name=帝王鳄内骨\nitem.claw.ceratosaurus.name=角鼻龙角\nitem.foot.triceratops.name=三角龙脚\nitem.foot.velociraptor.name=迅猛龙脚\nitem.foot.trex.name=霸王龙脚\nitem.foot.pterosaur.name=翼龙脚\nitem.foot.plesiosaur.name=蛇颈龙脚\nitem.foot.mosasaurus.name=沧龙脚\nitem.foot.liopleurodon.name=滑齿龙脚\nitem.foot.stegosaurus.name=剑龙脚\nitem.foot.dilophosaurus.name=双脊龙脚\nitem.foot.brachiosaurus.name=腕龙脚\nitem.foot.spinosaurus.name=脊龙脚\nitem.foot.compsognathus.name=美颌龙脚\nitem.foot.ankylosaurus.name=背甲龙脚\nitem.foot.pachycephalosaurus.name=肿头龙脚\nitem.foot.deinonychus.name=恐爪龙脚\nitem.foot.gallimimus.name=似鸡龙脚\nitem.foot.allosaurus.name=异特龙脚\nitem.foot.sarcosuchus.name=帝王鳄脚\nitem.foot.ceratosaurus.name=角鼻龙脚\nitem.skull.triceratops.name=三角龙头骨\nitem.skull.velociraptor.name=迅猛龙头骨\nitem.skull.trex.name=霸王龙头骨\nitem.skull.pterosaur.name=翼龙头骨\nitem.skull.plesiosaur.name=蛇颈龙头骨\nitem.skull.mosasaurus.name=沧龙头骨\nitem.skull.liopleurodon.name=滑齿龙头骨\nitem.skull.stegosaurus.name=剑龙头骨\nitem.skull.dilophosaurus.name=双脊龙头骨\nitem.skull.brachiosaurus.name=腕龙头骨\nitem.skull.spinosaurus.name=脊龙头骨\nitem.skull.compsognathus.name=美颌龙头骨\nitem.skull.ankylosaurus.name=背甲龙头骨\nitem.skull.pachycephalosaurus.name=肿头龙头骨\nitem.skull.deinonychus.name=恐爪龙头骨\nitem.skull.gallimimus.name=似鸡龙头骨\nitem.skull.allosaurus.name=异特龙头骨\nitem.skull.sarcosuchus.name=帝王鳄头骨\nitem.skull.ceratosaurus.name=角鼻龙头骨\nitem.vertebrae.triceratops.name=三角龙脊椎骨\nitem.vertebrae.velociraptor.name=迅猛龙脊椎骨\nitem.vertebrae.trex.name=霸王龙脊椎骨\nitem.vertebrae.pterosaur.name=翼龙脊椎骨\nitem.vertebrae.plesiosaur.name=蛇颈龙脊椎骨\nitem.vertebrae.mosasaurus.name=沧龙脊椎骨\nitem.vertebrae.liopleurodon.name=滑齿龙脊椎骨\nitem.vertebrae.stegosaurus.name=剑龙脊椎骨\nitem.vertebrae.dilophosaurus.name=双脊龙脊椎骨\nitem.vertebrae.brachiosaurus.name=腕龙脊椎骨\nitem.vertebrae.spinosaurus.name=脊龙脊椎骨\nitem.vertebrae.compsognathus.name=美颌龙脊椎骨\nitem.vertebrae.ankylosaurus.name=背甲龙脊椎骨\nitem.vertebrae.pachycephalosaurus.name=肿头龙脊椎骨\nitem.vertebrae.deinonychus.name=恐爪龙脊椎骨\nitem.vertebrae.gallimimus.name=似鸡龙脊椎骨\nitem.vertebrae.allosaurus.name=异特龙脊椎骨\nitem.vertebrae.sarcosuchus.name=帝王鳄脊椎骨\nitem.vertebrae.ceratosaurus.name=角鼻龙脊椎骨\nitem.dinoribcage.triceratops.name=三角龙胸肋骨\nitem.dinoribcage.velociraptor.name=迅猛龙胸肋骨\nitem.dinoribcage.trex.name=霸王龙胸肋骨\nitem.dinoribcage.pterosaur.name=翼龙胸肋骨\nitem.dinoribcage.plesiosaur.name=蛇颈龙胸肋骨\nitem.dinoribcage.mosasaurus.name=沧龙胸肋骨\nitem.dinoribcage.liopleurodon.name=滑齿龙胸肋骨\nitem.dinoribcage.stegosaurus.name=剑龙胸肋骨\nitem.dinoribcage.dilophosaurus.name=双脊龙胸肋骨\nitem.dinoribcage.brachiosaurus.name=腕龙胸肋骨\nitem.dinoribcage.spinosaurus.name=脊龙胸肋骨\nitem.dinoribcage.compsognathus.name=美颌龙胸肋骨\nitem.dinoribcage.ankylosaurus.name=背甲龙胸肋骨\nitem.dinoribcage.pachycephalosaurus.name=肿头龙胸肋骨\nitem.dinoribcage.deinonychus.name=恐爪龙胸肋骨\nitem.dinoribcage.gallimimus.name=似鸡龙胸肋骨\nitem.dinoribcage.allosaurus.name=异特龙胸肋骨\nitem.dinoribcage.sarcosuchus.name=帝王鳄胸肋骨\nitem.dinoribcage.ceratosaurus.name=角鼻龙胸肋骨\nitem.dinosaurmodels.triceratops.name=三角龙模型\nitem.dinosaurmodels.velociraptor.name=迅猛龙模型\nitem.dinosaurmodels.trex.name=霸王龙模型\nitem.dinosaurmodels.pterosaur.name=翼龙模型\nitem.dinosaurmodels.plesiosaur.name=蛇颈龙模型\nitem.dinosaurmodels.mosasaurus.name=沧龙模型\nitem.dinosaurmodels.liopleurodon.name=滑齿龙模型\nitem.dinosaurmodels.stegosaurus.name=剑龙模型\nitem.dinosaurmodels.dilophosaurus.name=双脊龙模型\nitem.dinosaurmodels.brachiosaurus.name=腕龙模型\nitem.dinosaurmodels.spinosaurus.name=脊龙模型\nitem.dinosaurmodels.compsognathus.name=美颌龙模型\nitem.dinosaurmodels.ankylosaurus.name=背甲龙模型\nitem.dinosaurmodels.pachycephalosaurus.name=肿头龙模型\nitem.dinosaurmodels.deinonychus.name=恐爪龙模型\nitem.dinosaurmodels.gallimimus.name=似鸡龙模型\nitem.dinosaurmodels.allosaurus.name=异特龙模型\nitem.dinosaurmodels.sarcosuchus.name=帝王鳄模型\nitem.dinosaurmodels.ceratosaurus.name=角鼻龙模型\nitem.plantfossil.name=植物化石\nitem.skullhelmet.name=颅骨头盔\nitem.ribcage.name=肋骨之笼\nitem.shinguards.name=护胫\nitem.feet.name=一对脚掌\nitem.amber.name=琥珀\nitem.ancientvase.name=古代瓶子\nitem.ancientvasebroken.name=破损的古代瓶子\nitem.bonearrow.name=骨制箭矢\nitem.bonebow.name=骨弓\nitem.boneglue.name=骨胶\nitem.bonerod.name=骨头棍\nitem.bonesword.name=骨剑\nitem.powderystring.name=粉化丝线\nitem.animalcoin.name=动物硬币\nitem.dinocoin.name=恐龙硬币\nitem.dodowing.name=生渡渡鸟翅膀\nitem.dodowingcooked.name=渡渡鸟烤翅\nitem.rawconfuciornis.name=生孔子鸟\nitem.cookedconfuciornis.name=熟孔子鸟\nitem.dinosteak.name=恐龙肉排\nitem.rawtriceratops.name=三角龙肉\nitem.rawvelociraptor.name=迅猛龙肉\nitem.rawtrex.name=霸王龙肉\nitem.rawpterosaur.name=翼龙肉\nitem.rawnautilus.name=鹦鹉螺肉\nitem.rawplesiosaur.name=蛇颈龙肉\nitem.rawmosasaurus.name=沧龙肉\nitem.rawliopleurodon.name=滑齿龙肉\nitem.rawstegosaurus.name=剑龙肉\nitem.rawdilophosaurus.name=双脊龙肉\nitem.rawbrachiosaurus.name=腕龙肉\nitem.rawspinosaurus.name=脊龙肉\nitem.rawcompsognathus.name=美颌龙肉\nitem.rawankylosaurus.name=背甲龙肉\nitem.rawpachycephalosaurus.name=肿头龙肉\nitem.rawdeinonychus.name=恐爪龙肉\nitem.rawgallimimus.name=似鸡龙肉\nitem.rawallosaurus.name=异特龙肉\nitem.rawsarcosuchus.name=帝王鳄肉\nitem.rawceratosaurus.name=角鼻龙肉\nitem.eggtriceratops.name=三角龙蛋\nitem.eggvelociraptor.name=迅猛龙蛋\nitem.eggtrex.name=霸王龙蛋\nitem.eggpterosaur.name=翼龙蛋\nitem.eggnautilus.name=活体鹦鹉螺\nitem.eggplesiosaur.name=蛇颈龙蛋\nitem.eggmosasaurus.name=沧龙蛋\nitem.eggliopleurodon.name=滑齿龙蛋\nitem.eggstegosaurus.name=剑龙蛋\nitem.eggdilophosaurus.name=双脊龙蛋\nitem.eggbrachiosaurus.name=腕龙蛋\nitem.eggspinosaurus.name=脊龙蛋\nitem.eggcompsognathus.name=美颌龙蛋\nitem.eggdodo.name=渡渡鸟蛋\nitem.eggcultivateddodo.name=人工养殖渡渡鸟蛋\nitem.eggankylosaurus.name=背甲龙蛋\nitem.eggpachycephalosaurus.name=肿头龙蛋\nitem.eggdeinonychus.name=恐爪龙蛋\nitem.egggallimimus.name=似鸡龙蛋\nitem.eggallosaurus.name=异特龙蛋\nitem.eggsarcosuchus.name=帝王鳄蛋\nitem.eggceratosaurus.name=角鼻龙蛋\nitem.eggcoelacanth.first.name=海生腔棘鱼\nitem.eggcoelacanth.second.name=河生腔棘鱼\nitem.eggcoelacanth.third.name=沼泽腔棘鱼\nitem.eggterrorbird.gastornis.name=冠恐鸟蛋\nitem.eggterrorbird.phorusrhacos.name=恐鹤蛋\nitem.eggterrorbird.titanis.name=泰坦鸟蛋\nitem.eggterrorbird.kelenken.name=窃鹤蛋\nitem.eggcultivatedterrorbird.gastornis.name=人工养殖冠恐鸟蛋\nitem.eggcultivatedterrorbird.phorusrhacos.name=人工养殖恐鹤蛋\nitem.eggcultivatedterrorbird.titanis.name=人工养殖泰坦鸟蛋\nitem.eggcultivatedterrorbird.kelenken.name=人工养殖窃鹤蛋\nitem.eggcultivatedchicken.name=人工培育的鸡蛋\nitem.eggconfuciusornis.name=孔子鸟蛋\nitem.eggcultivatedconfuciusornis.name=人工培育的孔子鸟蛋\nitem.failuresaurusflesh.name=畸龙肉\nitem.dnatriceratops.name=三角龙DNA\nitem.dnavelociraptor.name=迅猛龙DNA\nitem.dnatrex.name=霸王龙DNA\nitem.dnapterosaur.name=翼龙DNA\nitem.dnanautilus.name=鹦鹉螺DNA\nitem.dnaplesiosaur.name=蛇颈龙DNA\nitem.dnamosasaurus.name=沧龙DNA\nitem.dnaliopleurodon.name=滑齿龙DNA\nitem.dnastegosaurus.name=剑龙DNA\nitem.dnadilophosaurus.name=双脊龙DNA\nitem.dnabrachiosaurus.name=腕龙DNA\nitem.dnaspinosaurus.name=脊龙DNA\nitem.dnacompsognathus.name=美颌龙DNA\nitem.dnaankylosaurus.name=背甲龙DNA\nitem.dnapachycephalosaurus.name=肿头龙DNA\nitem.dnadeinonychus.name=恐爪龙DNA\nitem.dnasarcosuchus.name=帝王鳄DNA\nitem.dnaceratosaurus.name=角鼻龙DNA\nitem.dnagallimimus.name=似鸡龙DNA\nitem.dnacoelacanth.name=腔棘鱼DNA\nitem.dnapig.name=猪DNA\nitem.dnasheep.name=羊DNA\nitem.dnacow.name=牛DNA\nitem.dnachicken.name=鸡DNA\nitem.dnasmilodon.name=剑齿虎DNA\nitem.dnamammoth.name=猛犸象DNA\nitem.dnadodo.name=渡渡鸟DNA\nitem.dnahorse.name=马DNA\nitem.dnaquagga.name=斑驴DNA\nitem.dnaterrorbird.name=恐鸟DNA\nitem.dnaallosaurus.name=异特龙DNA\nitem.dnaelasmotherium.name=板齿犀DNA\nitem.dnaconfuciusornis.name=孔子鸟DNA\nitem.embryopig.name=猪胚胎\nitem.embryosheep.name=羊胚胎\nitem.embryocow.name=牛胚胎\nitem.embryochicken.name=鸡胚胎\nitem.embryosmilodon.name=剑齿虎胚胎\nitem.embryomammoth.name=猛犸象胚胎\nitem.embryododo.name=渡渡鸟胚胎\nitem.embryohorse.name=马胚胎\nitem.embryoquagga.name=斑驴胚胎\nitem.embryoelasmotherium.name=板齿犀胚胎\nitem.archnotebook.name=考古手册\nitem.potteryshard.name=陶片\nitem.terrorbirdmeat.name=生恐鸟腿\nitem.terrorbirdmeatcooked.name=熟恐鸟腿\nitem.quaggameat.name=生斑驴肉\nitem.quaggameatcooked.name=熟斑驴肉\nitem.dominicanamber.name=多米尼加蓝琥珀\nitem.aquaticscarabgem.name=海蓝圣甲虫宝石\nitem.ancientkey.name=古代钥匙\nitem.ancientclock.name=古代时钟\nitem.toothdagger.name=牙制匕首\nitem.fossilseed_fern.name=Fossilized Fern Spores\nitem.fossilsapling_palae.name=Petrified Palaeoraphe Sapling\nitem.fernseeds.name=古代蕨类孢子\nitem.palae_fossil.name=古树树苗化石\nitem.fossilseed.dillhoffia.name=Dillhoffia种子化石\nitem.fossilseed.sarracina.name=瓶子草种子化石\nitem.fossilseed.cephalotaxus.name=三尖杉种子化石\nitem.fossilseed.licopodiophyta.name=石松门孢子化石\nitem.fossilseed.paleopanax.name=Foozia孢子化石\nitem.fossilseed.zamites.name=腹羽叶种子化石\nitem.fossilseed.bennettitales.name=本内苏铁种子化石\nitem.fossilseed.welwitschia.name=千岁兰种子化石\nitem.fossilseed.horsetail.name=马尾草孢子化石\nitem.seed.dillhoffia.name=Dillhoffia种子\nitem.seed.sarracina.name=瓶子草种子\nitem.seed.cephalotaxus.name=三尖杉种子\nitem.seed.licopodiophyta.name=石松门孢子\nitem.seed.paleopanax.name=Foozia孢子\nitem.seed.zamites.name=腹羽叶种子\nitem.seed.bennettitales.name=本内苏铁种子\nitem.seed.welwitschia.name=千岁兰种子\nitem.seed.horsetail.name=马尾草孢子\ntile.plant_dillhoffia.name=Dillhoffia\ntile.plant_sarracina.name=瓶子草\ntile.plant_cephalotaxus.name=三尖杉\ntile.plant_licopodiophyta.name=石松门\ntile.plant_paleopanax.name=Foozia\ntile.plant_zamites.name=腹羽叶\ntile.plant_bennettitales_small.name=本内苏铁\ntile.plant_bennettitales_large.name=高本内苏铁\ntile.plant_welwitschia.name=千岁兰\ntile.plant_horsetail_small.name=马尾草\ntile.plant_horsetail_large.name=高马尾草\ntile.plant_mutant.name=畸变植物\ndnaname.tail=DNA\nembryoname.tail=胚胎\nmeatname.tail=肉\nmgcname.head=神奇海螺:\nmgcname.tail=模式\ndeggname.tail=蛋\norder.head=命令:\norder.stay=留在原地\norder.follow=跟随\norder.freemove=自由移动\nstatus.hungry=饿了\nstatus.starve=饿死了\nstatus.learningchest.head=一头\nstatus.learningchest=学会了如何开箱子\nstatus.betrayed.head=这头\nstatus.betrayed=不再相信人類\nstatus.nospace=没有足够的空间成长\nstatus.starveesc=因为太饿而逃走了\nstatus.sjlbite=咬了烧酒螺后跑开了\nstatus.chewtime=需要时间来咀嚼\nstatus.full=吃饱了\nstatus.nervous.head=你让这头小\nstatus.nervous=太紧张以至于无法自行猎食\nstatus.gemerroryoung=这头霸王龙还太年轻了\nstatus.gemerrorhealth=圣甲虫宝石无法负荷如此强的生命能量\nstatus.gemerrortamed=这头霸王龙已被驯服\nstatus.essencefail=鸡精没有起效\nentity.fossil.triceratops.name=三角龙\nentity.fossil.velociraptor.name=迅猛龙\nentity.fossil.trex.name=霸王龙\nentity.fossil.pterosaur.name=翼龙\nentity.fossil.plesiosaur.name=蛇颈龙\nentity.fossil.mosasaurus.name=沧龙\nentity.fossil.liopleurodon.name=滑齿龙\nentity.fossil.stegosaurus.name=剑龙\nentity.fossil.dilophosaurus.name=双脊龙\nentity.fossil.brachiosaurus.name=腕龙\nentity.fossil.nautilus.name=鹦鹉螺\nentity.fossil.spinosaurus.name=脊龙\nentity.fossil.compsognathus.name=美颌龙\nentity.fossil.ankylosaurus.name=背甲龙\nentity.fossil.pachycephalosaurus.name=肿头龙\nentity.fossil.deinonychus.name=恐爪龙\nentity.fossil.gallimimus.name=似鸡龙\nentity.fossil.allosaurus.name=异特龙\nentity.fossil.sarcosuchus.name=帝王鳄\nentity.fossil.ceratosaurus.name=角鼻龙\nentity.fossil.sentrypigman.name=哨兵猪人\nentity.fossil.mammoth.name=猛犸象\nentity.fossil.smilodon.name=剑齿虎\nentity.fossil.pregnantcow.name=受孕牛\nentity.fossil.pregnantpig.name=受孕猪\nentity.fossil.pregnantsheep.name=受孕羊\nentity.fossil.pregnanthorse.name=受孕马\nentity.fossil.dodo.name=渡渡鸟\nentity.fossil.coelacanth.name=腔棘鱼\nentity.fossil.quagga.name=斑驴\nentity.fossil.terrorbird.name=恐鸟\nentity.fossil.elasmotherium.name=板齿犀\nentity.fossil.confuciusornis.name=孔子鸟\nentity.fossil.anubite.name=阿努\nentity.fossil.anudead.name=阿努\npedia.text.owner=主人:\npedia.text.chest=* 箱子\npedia.text.caution=---警告:危险---\npedia.text.rideable=* 可乘骑\npedia.text.weak=虚弱垂死\npedia.text.fly=* 可飞行\npedia.eggwet=潮湿\npedia.eggdry=干燥\npedia.eggcold=寒冷\npedia.eggwarm=温暖\npedia.eggstatus=状态\npedia.eggprogress=孵化进度\npedia.eggday=天\npedia.eggdays=天\npedia.embryo.inside=怀有胎儿:\npedia.embryo.growing=成长进度:\npedia.embryo.pig=猪\npedia.embryo.sheep=羊\npedia.embryo.cow=牛\npedia.embryo.chicken=鸡\npedia.embryo.smilodon=剑齿虎\npedia.embryo.mammoth=猛犸象\npedia.embryo.dodo=渡渡鸟\npedia.embryo.horse=马\npedia.embryo.quagga=斑驴\npedia.embryo.elasmotherium=Elasmotherium\nanuspeaker.self=阿努:\nanuspeaker.hello=跪下吧,反抗无用.\nanuspeaker.barehand=空手吗... 愚蠢至极,但勇气可嘉.\nanuspeaker.draw=拔剑吧,勇士.\nanuspeaker.coward=用弓的胆小鬼!滚出来!\nanuspeaker.learthere=尝尝我在这里学会了什么吧!\nanuspeaker.leartthere=尝尝我在那里学会了什么吧!\nanuspeaker.unknownranged=所以那就是你的武器?\nanuspeaker.unknownmelee=哈!别闹了!\nanuspeaker.summon=为我卖命吧,我的仆人.\nanuspeaker.trans=地上的兽啊,显露你的智慧吧.\nanuspeaker.qi=剑气!\nanuspeaker.firerain=来下点火雨吧!\nanuspeaker.mysword=想要用魔法对抗我?真是愚蠢.\nanuspeaker.fewbeaten=没人能打败我,你也准备受死吧!\nanuspeaker.archers=弓箭手,放箭!\nanuspeaker.blaze=烈焰人!消灭这些敌人!\nanuspeaker.no=不!!!\nfpzspeaker.self=僵尸猪人:\nfpzspeaker.selfkill=离开了我皇的领导俺们活不了!\nfpzspeaker.lifefor.head=为\nfpzspeaker.lifefor.tail=而生!\nfpzspeaker.anusommon=我皇阿努万岁!!\ndinoegg.hatched=有颗恐龙蛋孵化了!\ndinoegg.nospace=这颗蛋无法放在这里.\ndinoegg.head=某颗\ndinoegg.dry=蛋因为太干燥死亡了\ndinoegg.cold=蛋因为太寒冷死亡了\ncultivate.outbreak=警告!培养槽失控!\ndrum.trigger=命令鼓模式:\ndrum.ordering=正在命令\ndrum.trex1=正在命令半径50格内的霸王龙来吃早餐\ndrum.trex2=正在命令半径50格内的霸王龙来吃午餐\ndrum.trex3=正在命令半径50格内的霸王龙来吃晚餐\nentity.fossil.bones.name=骨架\nentity.fossil.friendlypigzombie.name=僵尸猪人伙伴\nentity.fossil.failuresaurus.name=畸龙\nentity.fossil.pigboss.name=阿努\nitem.record_bones.name=化石唱片\nitem.record_bones_disc.name=化石唱片\nitem.record.record_bones_disc.desc=WhiteJoshMan-骨之唱片\nitem.record.music.anu.desc=Nanotyrano - Awakening\n'

    s = io.BytesIO(text.encode())
    s.seek(0)

    response = make_response(send_file(s, mimetype="text/plain", cache_timeout=0))
    response.headers["Content-Disposition"] = "attachment; filename=zh_CN.lang;"
    return response


if __name__ == "__main__":
    app.run('0.0.0.0')
