#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Weijie Zhang
"""Run FindNet's logic tests against the real code in app/index.html.

The app is a single HTML file, so this script pulls the functions it needs
straight out of that file and runs them under Node (20 or newer).
Usage:  python3 tests/run_tests.py
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = open(os.path.join(ROOT, "app", "index.html"), encoding="utf-8").read()
JS = HTML.split("<script>", 1)[1].rsplit("</script>", 1)[0]

def _scan(src, i, stop_on_semicolon):
    """Return the index just past a balanced block or statement starting at i."""
    depth, opened, q = 0, False, None
    while i < len(src):
        c = src[i]
        if q:
            if c == "\\": i += 2; continue
            if c == q: q = None
        elif c == "\\": i += 2; continue          # escaped char outside strings (regex literals)
        elif c in "\"'`": q = c
        elif c in "([{": depth += 1; opened = True
        elif c in ")]}":
            depth -= 1
            if not stop_on_semicolon and opened and depth == 0: return i + 1
        elif c == ";" and stop_on_semicolon and depth == 0: return i + 1
        i += 1
    raise ValueError("unbalanced source")

def fn(name):
    i = JS.index("function " + name + "(")
    if JS[max(0, i - 6):i] == "async ": i -= 6
    return JS[i:_scan(JS, JS.index("{", JS.index(")", i)), False)] + "\n"

def var(name):
    i = JS.index("var " + name + "=")
    return JS[i:_scan(JS, i, True)] + "\n"

def between(a, b):
    i = JS.index(a); return JS[i:JS.index(b, i)]

PRELUDE = """
Object.defineProperty(globalThis,"navigator",{value:{languages:["en-US"]},configurable:true});
Object.defineProperty(globalThis,"localStorage",{value:{getItem:()=>null,setItem:()=>{}},configurable:true});
let FAILS=0; const ok=(c,l)=>{ if(!c) FAILS++; console.log((c?"  PASS  ":"  FAIL  ")+l); };
"""
I18N = "".join(var(v) for v in ["MON","MONL","LANG","I18N_HANS","I18N_HANT","I18N_EN"]) + fn("T")
CONSTS = "".join(var(v) for v in ["MET","ACTS","ACTS_D","SIZES","DOGSIZE","DOGSIZE_SHORT","TEMPER","BREEDS"])
TEXT = var("TITLE_KEYS") + "".join(fn(f) for f in ["titleKeys","enEq","canonFrom","canonTitle","dispTitle","canonBreed","dispBreed","metOf","cleanNick"])
DATES = "".join(fn(f) for f in ["pad","dstr","addDays","today","atDay","monday","daysIn","myLog","weekInfo","monthInfo"])
SANITIZE = "function sanitize(s){" + between('DB.collection("dogs").onSnapshot(function(s){', "dogsBy=m; render();").split("{",1)[1] + " return m; }\n"
CRYPTO = "".join(fn(f) for f in ["b64","unb64","aesWith","enc","dec"])

SUITES = {}

SUITES["encryption (per-friend status + chat)"] = PRELUDE + CRYPTO + r"""
let KP=null, pubKeys={}, aesCache={};
const s=crypto.subtle;
async function user(){                       // generate, store as JSON, re-import: the same path ensureKeys() takes
  const kp=await s.generateKey({name:"ECDH",namedCurve:"P-256"},true,["deriveKey"]);
  const pj=await s.exportKey("jwk",kp.privateKey), uj=await s.exportKey("jwk",kp.publicKey);
  const stored=JSON.parse(JSON.stringify({priv:{kty:"EC",crv:"P-256",x:pj.x,y:pj.y,d:pj.d},pub:{kty:"EC",crv:"P-256",x:uj.x,y:uj.y}}));
  return {priv:await s.importKey("jwk",stored.priv,{name:"ECDH",namedCurve:"P-256"},false,["deriveKey"]),pub:stored.pub};
}
const U={A:await user(),B:await user(),C:await user()};
pubKeys={A:U.A.pub,B:U.B.pub,C:U.C.pub};
const as=id=>{ KP=U[id]; aesCache={}; };
const status={acts:{act1:true},here:{act1:"2026-10-01T08:02:00Z"}}, msg={text:"明天七点，滨江公园东门见 👋",t:"2026-10-01T08:05:00Z"};
as("A"); const share=await enc("B",status), note=await enc("B",msg);
as("B"); ok(JSON.stringify(await dec("A",share))===JSON.stringify(status),"a friend can read your encrypted status");
         ok((await dec("A",note))?.text===msg.text,"a friend can read your message (Chinese + emoji)");
as("A"); ok((await dec("B",note))?.text===msg.text,"you can re-read your own sent message");
as("C"); ok(await dec("A",share)===null,"someone else (or a blocked person) cannot read your status");
         ok(await dec("B",note)===null,"someone else cannot read a message between two friends");
as("B"); ok(await dec("A",{iv:note.iv,ct:note.ct.slice(0,-4)+"AAAA"})===null,"a tampered message is rejected");
ok(await enc("nobody",status)===null,"no message can be sent to someone without a key");
"""

SUITES["weekly / monthly active days"] = PRELUDE + DATES + r"""
const RealDate=Date; let NOW="2026-09-30T10:00:00";
globalThis.Date=class extends RealDate{ constructor(...a){ super(...(a.length?a:[NOW])); } };
let acts=[], weight=70, myState={acts:{
  a1:{day:"2026-09-28",mins:60,met:3.0}, a2:{day:"2026-09-28",mins:30,met:5.0}, a3:{day:"2026-09-30",mins:45,met:4.3},
  a4:{day:"2026-09-22",mins:60,met:3.0}, a5:{day:"2026-09-23",mins:60,met:3.0}, a6:{day:"2026-10-02",mins:60,met:3.0}, a7:true }};
let log=myLog(), w=weekInfo(log), m=monthInfo(log,"2026-09");
ok(log.length===5,"history keeps past entries, skips future ones and orphaned old records");
ok(w.n===2&&w.prev===2,"this week counts 2 days (two activities on one day = one day)");
ok(w.cells.map(c=>c.on?1:0).join("")==="1010000","week strip runs Monday to Sunday");
ok(m.days===4&&m.n===5&&m.mins===255,"September: 4 days, 5 activities, 255 minutes");
ok(m.kcal===Math.round(70*(3*1+5*.5+4.3*.75+3*1+3*1)),"calorie estimate = MET x weight x hours");
NOW="2026-10-01T09:00:00"; log=myLog();
ok(weekInfo(log).n===2&&monthInfo(log,"2026-10").days===0,"a week can span two months");
NOW="2026-10-04T20:00:00"; w=weekInfo(myLog());
ok(w.cells[0].ds==="2026-09-28"&&w.cells[6].today&&w.n===3,"Sunday closes the week that began Monday");
acts=[{id:"a3",day:"2026-09-30",mins:90,met:4.3}];
ok(monthInfo(myLog(),"2026-09").mins===300,"live activity details take priority over the saved copy");
"""

SUITES["dog profiles and size matching"] = PRELUDE + I18N + CONSTS + TEXT + fn("fits") + fn("dogsOf") + fn("dogOwnerLine") + SANITIZE + r"""
let dogsBy={};
ok(fits("s","small")&&!fits("m","small")&&!fits("l","small"),"small-dogs-only admits only small dogs");
ok(!fits("s","big")&&fits("m","big")&&fits("l","big")&&fits("s","any"),"medium/large and all-sizes rules");
dogsBy=sanitize({docs:[
  {id:"u1",data:()=>({list:[{name:"  豆豆 ",breed:"柯基",size:"s",temper:"friendly",vax:true,extra:"<b>x</b>"}]})},
  {id:"u2",data:()=>({list:[{name:"一只名字特别特别特别长的狗狗呀",size:"huge",temper:"evil",vax:"yes"},null,"str",{name:"B"},{name:"C"},{name:"D"}]})},
  {id:"u3",data:()=>({list:"not an array"})}]});
ok(dogsBy.u1[0].name==="豆豆"&&!("extra" in dogsBy.u1[0]),"other people's dog data is trimmed and unknown fields dropped");
ok(dogsBy.u2.length===3&&dogsBy.u2[0].name.length===12&&dogsBy.u2[0].size===""&&dogsBy.u2[0].vax===false,"bad values rejected, max 3 dogs, names capped");
ok(!("u3" in dogsBy),"malformed records are ignored");
LANG="hans"; ok(dogOwnerLine("u1")==="豆豆（柯基）的主人","owner line in Simplified");
LANG="hant"; ok(dogOwnerLine("u1")==="豆豆（柯基）的主人","owner line in Traditional");
LANG="en";   ok(dogOwnerLine("u1")==="Owner of 豆豆 (Corgi)","owner line in English, breed translated, name kept");
ok(dogOwnerLine("nobody")==="","no dogs, no line");
"""

SUITES["three languages"] = PRELUDE + I18N + CONSTS + TEXT + r"""
const keys=new Set(Object.keys(I18N_EN));
ok(Object.keys(I18N_HANT).every(k=>keys.has(k))&&[...keys].every(k=>k in I18N_HANT),"English and Traditional cover the same strings");
LANG="en";
ok(T("{n} 人参加",{n:1})==="1 person going"&&T("{n} 人参加",{n:4})==="4 people going","English plurals");
ok(T("{m}月{d}日",{m:10,d:5})==="Oct 5"&&T("{y}年{m}月",{y:2026,m:10})==="October 2026","English dates");
ok(T("rel:好友")==="Friend"&&T("好友")==="Friends","a tab name and a label can translate differently");
ok(T("遇到紧急情况请立即拨打 911。").includes("911"),"emergency number is 911");
LANG="hant";
ok(T(" · {n} 只狗狗",{n:3})===" · 3 隻狗狗"&&T("屏蔽 TA")==="封鎖 TA"&&T("周三")==="週三","Traditional uses 隻, 封鎖, 週");
LANG="hans"; ok(T("不存在的键")==="不存在的键","unknown text falls back to itself");
LANG="en";
ok(canonTitle("morning WALK")==="晨间散步"&&canonTitle("晨間散步")==="晨间散步","activity names typed in any language are stored the same way");
ok(dispTitle("广场舞")==="Square dancing"&&dispTitle("去中国超市买菜")==="去中国超市买菜","known kinds translate, free text stays as typed");
ok(canonBreed("Shiba Inu")==="柴犬"&&dispBreed("Goldendoodle")==="Goldendoodle","breeds round-trip; unknown breeds stay as typed");
ok(metOf(canonTitle("Square dancing"))===5.0,"calorie estimates still find the right activity");
"""

def main():
    total_fail = 0
    for name, code in SUITES.items():
        code += '\nif(FAILS) process.exitCode=1;\n'
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
            f.write(code); path = f.name
        print(name)
        r = subprocess.run(["node", path], capture_output=True, text=True)
        os.unlink(path)
        sys.stdout.write(r.stdout)
        if r.returncode:
            total_fail += 1
            if r.stderr.strip(): print("  ERROR  " + r.stderr.strip().splitlines()[-1])
    print("\nall suites passed" if not total_fail else f"\n{total_fail} suite(s) failed")
    sys.exit(1 if total_fail else 0)

if __name__ == "__main__":
    main()
