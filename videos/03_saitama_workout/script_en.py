# Saitama workout — English script (estimated timings, ~2.7 words/s, before the voice)
_L = [
# hook
"One hundred push-ups. One hundred sit-ups. One hundred squats. And a ten kilometer run.",
"Every single day.",
"This is the most famous workout in anime.",
"The hero who did it says it made him the strongest man alive, and cost him every hair on his head.",
"So what happens if a normal person actually does it?",
"And here's the question: one part of this program is almost useless. Can you guess which one?",
"Stick around. The answer might surprise you.",
# rules
"The rules are simple. Four exercises.",
"No weights. No gym. No days off.",
"Thirty days in a row.",
# week 1
"Day one. Push-ups.",
"The first twenty feel easy.",
"By thirty, the form breaks down. Hips sag, elbows flare, and every rep gets uglier.",
"The fix: split it up. Ten sets of ten, with short breaks. Same hundred reps, clean form.",
"Then come one hundred squats, and the legs start burning around rep sixty.",
"Then the sit-ups. Then the run.",
"Next morning, everything hurts.",
"That soreness is muscle damage from a load your body has never seen.",
"In the first week you actually feel weaker, not stronger. Your body is still repairing.",
# weeks 2-3
"By week two, something changes.",
"The push-ups get clean. The squats stop burning.",
"Your heart, lungs and muscles adapt to the volume fast.",
"Ten kilometers a day is around seventy kilometers a week. That burns a lot of fat.",
"And now, the answer. The almost useless part? The sit-ups.",
"Your abs are already there. They're just hidden under a layer of fat.",
"A hundred sit-ups won't burn the belly fat on top of them. The running and your diet will.",
"And here's the real problem with the whole program.",
"After two weeks, a hundred reps is no longer a challenge. It's endurance work.",
"Muscles grow from progressive overload. When the work never gets harder, the growth stops.",
# day 30
"Day thirty.",
"Body fat is down, mostly thanks to the running.",
"Endurance went through the roof.",
"Muscle? A little more. But nowhere near a superhero.",
"And the hair? Still there. No study links push-ups to hair loss.",
# better version
"So here's how to make this workout actually work.",
"One: swap plain push-ups for harder versions. Feet on a box, slower reps, fewer but tougher sets.",
"Two: replace sit-ups with planks and leg raises. They train the whole core, not just the top of your abs.",
"Three: take one or two rest days a week, and sleep. Muscles grow when you recover, not when you train.",
"And ten kilometers every day? Thirty to forty minutes of cardio is plenty.",
# ending
"You won't become the strongest hero in thirty days.",
"But you'll be stronger than you were yesterday. And that's the version that counts.",
"Write day one in the comments, and start tomorrow.",
]
SEG = []
_t = 0.0
for s in _L:
    SEG.append((round(_t, 2), s)); _t += len(s.split()) / 2.7 + 0.45
DUR = round(_t + 1.5, 1)
if __name__ == '__main__':
    print(len(SEG), 'segments', sum(len(s.split()) for _, s in SEG), 'words', DUR, 's')
    for t, s in SEG: print(t, s[:60])
