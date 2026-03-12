#!/bin/bash
# 每日英语短文自动推送
# 时间：每天早上 8:00
# 直接发送预置短文

# 获取今天日期
DATE=$(date +%Y-%m-%d)

# 短文内容（轮换发送）
case $(date +%u) in
  1)  # 周一
    ARTICLE="📚 每日英语短文 · $DATE · 周一

🏷️ 标题: The Power of Starting Small
🏷️ 难度: CET-4

📖 正文:
Every day, millions of people make a promise to themselves: \"I'll start tomorrow.\" Tomorrow becomes next week, next month, next year. But here's the truth — you don't need dramatic change. You need small, consistent habits.

Imagine you want to read more books. Don't commit to one book per week. That's overwhelming. Start with one page per day. That's it. One page. You can do that in two minutes. After a month, you've read 30 pages. After a year, you've read a dozen books.

The magic isn't in the action itself. It's in showing up. When you do something small every single day, it becomes part of who you are. Not something you have to think about. Not something that takes willpower. It just becomes automatic.

Think about exercise. You don't need to run a marathon. Just do 10 pushups. Or walk for 15 minutes. Small movements add up over time. Your body adapts. Your stamina builds.

The same principle applies to learning new skills. Want to learn a language? Study for 10 minutes daily. Want to code? Write 5 lines of code every day. Consistency beats intensity.

Success isn't about having more time or more money or more energy. It's about what you do with the small moments no one sees. It's about the compound effect of tiny actions repeated over and over.

So stop waiting for the perfect moment. Start small. Stay consistent. Trust the process. Your future self will thank you.

💡 核心词汇:
• promise /ˈprɒmɪs/ n. 承诺
• consistent /kənˈsɪstənt/ adj. 持续的
• willpower /ˈwɪlpaʊə(r)/ n. 意志力
• automatic /ˌɔːtəˈmætɪk/ adj. 自动的
• overwhelm /ˌəʊvəˈwelm/ v. 使不知所措
• stamina /ˈstæmɪnə/ n. 耐力
• compound /ˈkɒmpaʊnd/ v. 累积

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  2)  # 周二
    ARTICLE="📚 每日英语短文 · $DATE · 周二

🏷️ 标题: Why Morning Routines Matter
🏷️ 难度: CET-4

📖 正文:
What you do in the morning sets the tone for your entire day. The first hour after you wake up is crucial. It shapes your mindset, energy levels, and productivity for the hours that follow.

A consistent morning routine gives you structure. It reduces decision fatigue. When your routine is automatic, you don't waste mental energy thinking about what to do next. You just do it.

Successful people often share one thing in common: they protect their mornings. They wake up early enough to have quiet time. They exercise before checking emails. They plan their day before the world demands their attention.

Start with one small habit. Maybe it's drinking a glass of water immediately after waking up. Maybe it's five minutes of quiet thinking or meditation. Maybe it's writing in a journal.

Over time, build on that foundation. Add another small habit. Then another. The key is to start tiny and expand gradually.

The goal isn't perfection. The goal is progress. Your morning doesn't need to be complicated. It just needs to be consistent.

Tomorrow, try waking up 15 minutes earlier. Use that time for one positive habit. See how it changes your day.

💡 核心词汇:
• routine /ruːˈtiːn/ n. 惯例
• crucial /ˈkruːʃl/ adj. 关键的
• fatigue /fəˈtiːɡ/ n. 疲劳
• productive /prəˈdʌktɪv/ adj. 生产力高的
• protect /prəˈtekt/ v. 保护
• meditation /ˌmedɪˈteɪʃn/ n. 冥想
• foundation /faʊnˈdeɪʃn/ n. 基础

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  3)  # 周三
    ARTICLE="📚 每日英语短文 · $DATE · 周三

🏷️ 标题: The Art of Deep Work
🏷️ 难度: CET-4

📖 正文:
In a world full of distractions, the ability to focus is a superpower. Deep work is the ability to work without distraction on a cognitively demanding task. It's a skill that few people master, but anyone can develop.

The average person checks their phone every few minutes. They jump between tasks constantly. They never truly focus on anything for an extended period. This scattered approach to work feels productive, but it produces shallow results.

The most successful people protect their attention fiercely. They create time blocks for deep work. They say no to distractions. They treat their focus as a valuable resource to be invested wisely.

Start with 25 minutes of focused work. This is the Pomodoro technique. Close your phone. Disable notifications. Put away distractions. Sit down and work on one single task with full concentration.

At first, it will feel uncomfortable. Your mind will want to wander. You'll feel the urge to check something. But resist. Train your brain to stay present.

After a few sessions, you'll notice something change. Your ability to concentrate will improve. Your work quality will improve. You'll produce more in less time.

The shallow work fills your time. Deep work expands your capabilities.

💡 核心词汇:
• deep work /diːp wɜːk/ 深度工作
• distraction /dɪˈstrækʃn/ n. 干扰
• concentration /ˌkɒnsnˈtreɪʃn/ n. 专注
• cognitively /ˈkɒɡnɪtɪvli/ adv. 认知上
• scatter /ˈskætə(r)/ v. 分散
• fiercely /ˈfɪəsli/ adv. 激烈地
• capability /ˌkeɪpəˈbɪləti/ n. 能力

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  4)  # 周四
    ARTICLE="📚 每日英语短文 · $DATE · 周四

🏷️ 标题: Learning from Failure
🏷️ 难度: CET-4

📖 正文:
Everyone fails. It's an unavoidable part of life. From the moment we're born, we learn through trial and error. We fall down countless times before we learn to walk. Failure is not the opposite of success. It's part of the path to success.

But what separates successful people from others isn't avoiding failure. It's how they respond to failure. Winners don't quit when they fail. They analyze what went wrong. They extract the lesson. They try again with new wisdom.

When you experience failure, ask yourself these questions: What did I learn from this? How can I do better next time? What does this failure teach me about myself or my approach?

Every failure contains a lesson. Sometimes the lesson is about strategy. Sometimes it's about timing. Sometimes it's about mindset. Sometimes it's about the people you work with. The key is to extract that lesson and apply it.

Thomas Edison failed thousands of times before successfully inventing the light bulb. When asked about his failures, he said: \"I have not failed. I've just found 10,000 ways that won't work.\" That's the right attitude.

Don't let failure stop you. Let it teach you. Remember: success is not the absence of failure. It's the ability to keep going after failing.

💡 核心词汇:
• failure /ˈfeɪljə(r)/ n. 失败
• success /səkˈses/ n. 成功
• avoidable /əˈvɔɪdəbl/ adj. 可避免的
• trial /ˈtraɪəl/ n. 试验
• analyze /ˈænəlaɪz/ v. 分析
• extract /ɪkˈstrækt/ v. 提取
• attitude /ˈætɪtjuːd/ n. 态度

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  5)  # 周五
    ARTICLE="📚 每日英语短文 · $DATE · 周五

🏷️ 标题: Building Healthy Relationships
🏷️ 难度: CET-4

📖 正文:
Relationships are the foundation of a happy and meaningful life. Research consistently shows that strong social connections are one of the biggest predictors of happiness and health. But healthy relationships don't happen by accident. They require effort, communication, and trust.

Start by listening. Really listening. Not waiting for your your turn to speak. When someone talks to you, give them your full attention. Put away your phone. Make eye contact. Show them that what they say matters to you.

Then express yourself honestly. Share your feelings. Share your needs. Don't expect others to read your mind. Communication is a two-way street. You have to speak up if you want to be understood.

Also, be there for others. Support them in their challenges. Celebrate their wins. Comfort them in their losses. Relationships grow stronger through shared experiences and mutual support.

Remember that no relationship is perfect. There will be conflicts. There will be misunderstandings. The key is not avoiding conflict, but how you handle it. Approach disagreements with respect and a willingness to understand the other person's perspective.

Finally, invest time in your relationships. They're worth the effort. Call that friend you've been meaning to reach out to. Have dinner with your family. Spend quality time with the people who matter most.

💡 核心词汇:
• relationship /rɪˈleɪʃnʃɪp/ n. 关系
• foundation /faʊnˈdeɪʃn/ n. 基础
• connection /kəˈnekʃn/ n. 联系
• communication /kəˌmjuːnɪˈkeɪʃn/ n. 交流
• conflict /ˈkɒnflɪkt/ n. 冲突
• perspective /pəˈspektɪv/ n. 观点
• mutual /ˈmjuːtʃuəl/ adj. 相互的

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  6)  # 周六
    ARTICLE="📚 每日英语短文 · $DATE · 周六

🏷️ 标题: The Weekend Reset
🏷️ 难度: CET-4

📖 正文:
Weekends are for recharging your batteries. After a full week of work and responsibilities, you need time to rest and recover. How you spend your weekend can make or break your energy for the following week.

Sleep is essential. After a busy week, your body needs extra rest. Go to bed a little earlier if you can. But don't oversleep. Too much sleep can make you feel more tired. Find the balance that works for you.

Movement matters. Your body was designed to move. After sitting at a desk all week, get up and get active. Take a walk in nature. Go for a bike ride. Do some yoga. Exercise releases endorphins and boosts your mood.

Also, disconnect from work. Don't check work emails constantly. Don't bring work home mentally. Give yourself permission to step away completely. The world won't fall apart if you take two days off.

Spend time with loved ones. Connect with friends. Laughter and shared experiences strengthen relationships and improve wellbeing.

Do something you enjoy just for the fun of it. Read a book for pleasure. Watch a movie. Take a class. Learn something new. Follow your curiosity.

The goal is to start the new week feeling refreshed, recharged, and ready to tackle whatever comes your way.

💡 核心词汇:
• weekend /ˈwiːkend/ n. 周末
• recharge /ˌriːˈtʃɑːdʒ/ v. 充电
• essential /ɪˈsenʃl/ adj. 必要的
• endorphin /enˈdɔːfɪn/ n. 内啡肽
• disconnect /ˌdɪskəˈnekt/ v. 断开
• wellbeing /ˌwelˈbiːɪn/ n. 幸福
• curiosity /ˌkjʊəriˈɒsəti/ n. 好奇心

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
  0)  # 周日
    ARTICLE="📚 每日英语短文 · $DATE · 周日

🏷️ 标题: Planning for the Week Ahead
🏷️ 难度: CET-4

📖 正文:
Sundays are perfect for planning the week ahead. Taking time to think strategically about your week can dramatically increase your productivity and reduce stress. Without a plan, it's easy to drift through the week reacting to whatever comes up.

Start by reviewing your goals. What do you want to achieve this week? What are your most important objectives? Write them down. Something powerful happens when you put your goals in writing.

Next, identify your top three priorities. These are the tasks that will make the biggest difference. Focus on completing these first before moving to less important items.

Block time in your calendar for deep work. Protect those time blocks fiercely. Treat them as appointments with yourself that can't be moved. During these blocks, eliminate distractions and focus completely.

Also, prepare for challenges. What obstacles might you face this week? What problems might come up? Think about how you'll handle them. Having a plan B prevents stress when unexpected issues arise.

Prepare your workspace. Clean your desk. Gather the materials you need. Set up your tools. A little preparation goes a long way.

Finally, take a few minutes to visualize your ideal week. Imagine yourself being productive, calm, and successful. This mental rehearsal programs your brain for success.

A little planning on Sunday creates a much more productive week.

💡 核心词汇:
• strategy /ˈstrætədʒi/ n. 策略
• dramatically /drəˈmætɪkli/ adv. 显著地
• priority /praɪˈɒrəti/ n. 优先级
• objective /əbˈdʒektɪv/ n. 目标
• obstacle /ˈɒbstəkl/ n. 障碍
• visualization /ˌvɪʒuəlaɪˈzeɪʃn/ n. 可视化
• rehearsal /rɪˈhɜːsl/ n. 排练

━━━━━━━━━━━━━━━
每天进步一点点 🇺🇸"
    ;;
esac

# 发送到飞书群
openclaw message send --channel feishu --target "chat:oc_f84f0158693c8887be1bac624f143805" --message "$ARTICLE"

echo "$(date): English article sent" >> /tmp/cron_english.log
