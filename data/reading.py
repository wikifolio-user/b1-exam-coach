"""Original practice sets following the six B1 Preliminary Reading formats."""


def _question(set_id, part, number, prompt, options, answer, explanation, accepted=None):
    question = {
        "id": f"{set_id}-q{number}",
        "skill": "Reading",
        "topic": f"Part {part}",
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }
    if accepted:
        question["accepted_answers"] = accepted
    return question


def _set(set_id, part, title, instructions, passage, items):
    return {
        "id": set_id,
        "part": part,
        "title": title,
        "instructions": instructions,
        "passage": passage.strip(),
        "questions": [
            _question(set_id, part, index, *item)
            for index, item in enumerate(items, start=1)
        ],
    }


READING = [
    _set(
        "reading-p1-everyday", 1, "Everyday messages",
        "Read the five short messages. Choose the meaning that matches each message.",
        """
1. LIBRARY NOTICE
On Friday the library will close at 4 p.m. while we move the shelves. After 4, please put returned books in the box beside the entrance.

2. TEXT FROM MUM
Soup's in the fridge. Heat it up before eating. Don't wait for me — I won't be home until after nine.

3. TENNIS CLUB
Beginners can borrow a racket for Tuesday's lesson. Please reserve one by Monday evening.

4. MESSAGE FROM JOSH
Hi Ben! Tonight's film is sold out. I've reserved two tickets for Saturday instead. Let me know by six if that works for you.

5. ART ROOM NOTICE
Take your projects home on Friday. Anything still here after the weekend will be recycled.
""",
        [
            ("What does notice 1 tell library visitors?", ["Return books outside if the library has already closed.", "Keep all borrowed books until the shelves have been moved.", "Visit after four on Friday to borrow books."], "Return books outside if the library has already closed.", "The library closes early, but the box beside the entrance remains available for returns."),
            ("What does Mum want the reader to do in message 2?", ["Prepare soup for her when she comes home.", "Have the soup without waiting for her.", "Leave the soup out of the fridge until nine."], "Have the soup without waiting for her.", "Mum says 'Don't wait for me' and gives instructions for heating the soup."),
            ("What must a beginner do to borrow a racket in notice 3?", ["Ask for it before the day of the lesson.", "Buy it at Monday's lesson.", "Return it before Tuesday evening."], "Ask for it before the day of the lesson.", "A racket for Tuesday must be reserved by Monday evening."),
            ("Why has Josh sent message 4?", ["To ask Ben to collect tickets before six.", "To check whether Ben can go on a different day.", "To warn Ben that Saturday's film has sold out."], "To check whether Ben can go on a different day.", "Josh changed the booking from tonight to Saturday and asks whether the new day is suitable."),
            ("What should students do after reading notice 5?", ["Finish their projects during the weekend.", "Use recycled materials for their next projects.", "Collect their projects before they are thrown away."], "Collect their projects before they are thrown away.", "Projects left after the weekend will be recycled, so students should take them on Friday."),
        ],
    ),
    _set(
        "reading-p1-going-out", 1, "Going out and getting around",
        "Read the five short messages. Choose the meaning that matches each message.",
        """
1. CAFÉ SIGN
Today's soup is available to take away only. Our kitchen is open, but the seating area is being painted.

2. TRAIN STATION NOTICE
The lift to platform 2 is out of order. Passengers needing step-free access should ask staff for another route.

3. TEXT FROM LEILA
The band starts at eight, but let's meet at seven thirty outside the hall. I still need to collect our tickets.

4. COMMUNITY POOL
Children under twelve must swim with an adult, even if they have completed swimming lessons.

5. MESSAGE FROM ALEX
I can drive you to the airport on Sunday, but my car won't fit your big suitcase and mine. Could you use a smaller bag?
""",
        [
            ("What can customers do at the café in notice 1?", ["Buy soup to eat somewhere else.", "Eat soup inside once the kitchen closes.", "Sit down if they order something other than soup."], "Buy soup to eat somewhere else.", "Food is available, but the seating area is closed for painting."),
            ("Who should speak to staff after reading notice 2?", ["Anyone who wants to know the next train time.", "Anyone who cannot use the stairs to platform 2.", "Anyone who has left a bag in the lift."], "Anyone who cannot use the stairs to platform 2.", "'Step-free access' means a route without stairs; staff can provide an alternative to the broken lift."),
            ("Why does Leila want to arrive early in message 3?", ["To watch the band practise before the concert.", "To get the tickets before the music begins.", "To buy tickets for the next day's concert."], "To get the tickets before the music begins.", "Leila needs to collect the tickets before the band starts at eight."),
            ("What does notice 4 say about children under twelve?", ["They must take lessons before visiting the pool.", "They can swim alone if they have had lessons.", "They need an adult with them in the water."], "They need an adult with them in the water.", "The rule applies even to children who have already completed swimming lessons."),
            ("What is Alex asking the reader to do in message 5?", ["Find someone else to drive on Sunday.", "Take less luggage for the journey.", "Leave Alex's suitcase at home."], "Take less luggage for the journey.", "Alex offers a lift but asks for a smaller bag because there is not enough room for both large suitcases."),
        ],
    ),
    _set(
        "reading-p2-classes", 2, "Choose a community class",
        "For each person, choose the most suitable class, A–H. Use each letter at most once. Three classes are not needed.",
        """
A. Voices Together
Join our Wednesday evening singing group. You should already feel comfortable singing with others, but there is no need to read music or play an instrument. We practise popular songs and perform them at a small concert at the end of the month. Adults and teenagers over fourteen are welcome.

B. Keep Your Bike Moving
Learn to repair punctures, adjust brakes and look after your bicycle on Tuesday evenings. Bring your own bike and work with an experienced mechanic. This is a practical course for complete beginners. Tools are provided, and the tutor will explain which ones are worth buying later.

C. Grow a Better Garden
On Monday mornings, an expert gardener visits local gardens with our small group. Learn about flowers and soil, then plan a garden of your own. The course costs £45, including a workbook. It is aimed at people who already grow plants and want to develop their skills.

D. A Small Gift in Glass
Spend a Wednesday morning making a colourful mosaic coaster. No previous craft experience is needed. The £5 fee covers all materials, and you can take your work home at the end of the class. Our friendly tutor will help you choose a simple design for your first project.

E. Your First Short Film
This Thursday evening course shows you how to record and edit interviews indoors. We provide video cameras and computers, so a phone is not required. Students work in pairs to create a two-minute film about a person they know. The course is suitable for beginners over sixteen.

F. Better Pictures with Your Phone
Meet in Green Park every Saturday afternoon to explore light, colour and unusual angles. All photos are taken on your own smartphone. After a short demonstration, you will photograph trees, buildings and people outside. Beginners are welcome, and the tutor can help with basic phone settings.

G. Food from the Sea
Our Friday evening cooking course teaches adults to prepare simple fish meals. You will work in a professional kitchen and eat what you make. The tutor supplies ingredients, but please bring a container for any leftovers. This course is for people who already know basic cooking skills.

H. Family Plant-Based Kitchen
Children aged ten and over can attend this Saturday morning class with an adult family member. Each pair makes a vegetarian lunch together using beans, vegetables and fresh herbs. Beginners are welcome. Ingredients are provided, and everyone eats together before the class finishes.
""",
        [
            ("Nora wants to take better pictures on her phone. She is free at weekends and would like to learn outside.", list("ABCDEFGH"), "F", "F uses students' smartphones, takes place in a park and meets on Saturdays."),
            ("Ben has never repaired a bicycle. He wants to learn to look after his own bike and can attend on a weekday evening.", list("ABCDEFGH"), "B", "B teaches beginners bike maintenance on Tuesday evenings and asks them to bring their own bike."),
            ("Twenty-year-old Sara wants to cook a meat-free meal with her twelve-year-old brother. They are both beginners and are free on Saturday.", list("ABCDEFGH"), "H", "H welcomes children aged ten and over with an adult family member and teaches vegetarian cooking on Saturday."),
            ("Marta is a beginner who wants to make a present to take home. She can attend on a weekday morning and can spend only £10.", list("ABCDEFGH"), "D", "D offers a beginner craft project to take home on Wednesday morning for £5."),
            ("Leo enjoys singing and feels confident in a group. He cannot play an instrument and wants an evening class that leads to a performance.", list("ABCDEFGH"), "A", "A meets in the evening, requires no instrumental skills and finishes with a concert."),
        ],
    ),
    _set(
        "reading-p2-day-trips", 2, "Plan a day trip",
        "For each person, choose the most suitable day trip, A–H. Use each letter at most once. Three trips are not needed.",
        """
A. Hilltop Challenge
Leave early on Sunday for a demanding six-hour walk up Stone Hill. The path is steep and sometimes muddy, so strong boots and a good level of fitness are essential. A guide explains the area's geology. Bring lunch and enough drinking water; there are no cafés on the route.

B. Nature Under One Roof
The indoor Discovery Centre is a good choice whatever the weather. Children from age four can join a keeper to prepare food for small rescued animals. Families then follow a trail about animal homes. Sessions run on both weekend days and must be booked in advance.

C. Town History Museum
Our free museum opens every Sunday. A new exhibition brings Roman life to the town, with original objects and models of ancient streets. All galleries have wide, level entrances and a lift serves the upper floor. There is an accessible café and space to park mobility equipment.

D. Tastes of Riverside
On Saturday mornings, a local guide leads a gentle walk around the food market. Meet the stallholders and try dishes made in the region. A vegetarian tasting menu is available if requested when booking. The tour lasts two hours, with plenty of stops and a chance to buy ingredients.

E. Modern Art by the River
This gallery displays recent paintings and sculptures from local artists. It is open on Saturdays and Sundays, with step-free access throughout. Entry costs £12. A guide gives a talk about modern art every afternoon. Families can also book a painting workshop for children aged eight and over.

F. Birds from the Water
Watch ducks, herons and other wild birds from a small covered boat on the wetlands. A wildlife guide helps you use the binoculars supplied. The weekend trip lasts ninety minutes and requires no long walk. Only a few easy steps lead from the car park to the boat.

G. Ocean World
Visit sharks and colourful fish in our indoor aquarium. Special talks explain how oceans are changing. The children's workshop is designed for those aged eight and over and focuses on drawing sea creatures. Tickets include entry to the aquarium but workshops cost extra. Open every day.

H. The Old Railway Cycle Route
Spend Saturday following a flat, traffic-free route through villages and fields. Bring your own bicycle and a picnic. Our leader sets a relaxed pace, with stops to rest and explore. This is a full-day trip, beginning at ten and ending at five. Bike hire is not available.
""",
        [
            ("Eva uses a wheelchair and enjoys ancient history. She wants to go out on Sunday without paying an entrance fee.", list("ABCDEFGH"), "C", "C is free on Sundays, has Roman objects and provides step-free access to all galleries."),
            ("Tom wants to see wild birds with a guide. He likes boat trips but cannot manage a long or difficult walk.", list("ABCDEFGH"), "F", "F combines guided birdwatching with a boat trip and requires only a few easy steps."),
            ("The Park family needs an activity for a rainy weekend. Their youngest child is five and wants to help care for animals.", list("ABCDEFGH"), "B", "B is indoors and allows children from four to help prepare food for rescued animals."),
            ("Amina has her own bicycle and would like to spend a whole day outdoors. She is happy to bring her own lunch.", list("ABCDEFGH"), "H", "H is a full-day cycle trip that requires participants to bring a bike and picnic."),
            ("Luis is free on Saturday morning. He wants to learn about local food, taste it, and avoid dishes containing meat.", list("ABCDEFGH"), "D", "D is a Saturday morning local food tour and provides a vegetarian tasting menu."),
        ],
    ),
    _set(
        "reading-p3-roof-garden", 3, "A garden above the town",
        "Read the text. Choose the best answer for each of the five questions.",
        """
When the library manager suggested making a garden on the flat roof, sixteen-year-old Maya offered to help. She enjoyed being outdoors, but she had never grown anything. She was worried that the other volunteers would expect her to know more. At the first meeting, however, most of them had the same questions as she did.

The roof could be reached by a lift, and a building expert had checked that it was safe. There was still plenty to do. The group needed containers for the plants, but new ones were expensive. Maya suggested asking the café next door for its empty wooden boxes. The owner agreed, and the volunteers lined the boxes so water would not run out too quickly.

They decided to grow herbs and small vegetables rather than flowers. The café offered to buy some of the herbs, which would pay for seeds the following year. A gardener showed the group how much space each plant needed. Maya had thought putting lots of plants in every box would produce more food. She soon learnt that crowded plants did not grow well.

In July the weather became hot, and the plants needed water every day. The original plan was for everyone to arrive together on Saturday mornings. This was no longer enough. The volunteers made a timetable, and Maya took the Monday evening job because she could go after school. Once or twice she wanted to stay at home, but she knew the plants depended on her.

By September the roof looked completely different. People visiting the library began coming upstairs to sit beside the green boxes. Maya was proud of the vegetables, but the best part for her was meeting people of different ages. She still made mistakes, such as picking one tomato too early, yet she no longer worried about asking for advice. Next year she wants to help new volunteers feel as welcome as she did.
""",
        [
            ("Why was Maya nervous before the first meeting?", ["She thought the roof might be unsafe.", "She had very little gardening experience.", "She did not know where the library was.", "She was afraid nobody else would volunteer."], "She had very little gardening experience.", "Maya had never grown anything and worried others would expect her to know more."),
            ("How did Maya help the group save money?", ["She found somewhere to borrow tools.", "She persuaded the gardener to work for free.", "She suggested reusing boxes from a nearby business.", "She offered to pay for all the seeds."], "She suggested reusing boxes from a nearby business.", "Maya proposed using the café's empty wooden boxes instead of buying new containers."),
            ("What did Maya learn about growing plants?", ["Plants need enough room to grow well.", "Flowers are always easier to grow than vegetables.", "Herbs should be watered only once a week.", "Every type of vegetable needs the same care."], "Plants need enough room to grow well.", "She discovered that crowded plants did not grow well."),
            ("Why did the volunteers change their working arrangements in July?", ["The library stopped opening on Saturdays.", "The café needed larger amounts of herbs.", "Several volunteers had left the group.", "The plants needed more frequent attention."], "The plants needed more frequent attention.", "Hot weather meant daily watering, so the weekly Saturday meeting was no longer sufficient."),
            ("Which message would Maya most likely send a friend now?", ["'The vegetables were great, but I wish I'd worked alone.'", "'You should join us; people are happy to help you learn.'", "'Don't join unless you already know a lot about gardening.'", "'I enjoyed it, but I'm too embarrassed to go back next year.'"], "'You should join us; people are happy to help you learn.'", "Maya values the people she met, now asks for advice and wants to welcome new volunteers."),
        ],
    ),
    _set(
        "reading-p3-repair-club", 3, "Fixing things together",
        "Read the text. Choose the best answer for each of the five questions.",
        """
For years, Daniel threw broken objects away without thinking much about them. Then his desk lamp stopped working just before an important school project. He could not afford a new one, and a friend told him about the repair club at the community centre. Daniel expected to leave the lamp there and collect it later. Instead, the volunteers invited him to sit beside them and help.

The club met twice a month. People brought small electrical objects, clothes and toys, and worked with volunteers who had useful skills. There was no charge, although visitors could put money in a box to help buy materials. Nobody promised that every object could be repaired. For safety reasons, the volunteers first checked electrical items and only let visitors do tasks suitable for them.

Daniel's lamp needed a new switch. While a trained volunteer dealt with the wires, Daniel cleaned the lamp and watched carefully. An hour later it worked again. What surprised him most was how much he had learnt by asking questions. He began taking other objects to the club, including a jacket with a broken zip.

After several visits, Daniel asked whether he could become a volunteer. He still knew very little about electrical repairs, so the organiser suggested starting somewhere else. Daniel was good at explaining things and enjoyed meeting people. Now he welcomes visitors, writes down what they have brought and shows them where to wait. He is also learning to mend clothes from another volunteer.

The club recently held an open day. Daniel made posters for his school and invited classmates to bring something broken. Many thought repairing an old object would take too much time. But once they had seen a favourite toy or pair of jeans repaired, they understood why it could be worthwhile.

Daniel does not think people should feel guilty whenever they buy something new. He simply wants them to consider repairing things first. 'You save money, learn a skill and keep something you like,' he says. 'It also feels good to solve a problem with other people.'
""",
        [
            ("What had Daniel expected on his first visit?", ["To do every part of the repair himself.", "To exchange his lamp for another one.", "To leave his lamp for someone else to repair.", "To pay for a course in electrical repairs."], "To leave his lamp for someone else to repair.", "He expected to leave the lamp at the club and collect it later, but was invited to help."),
            ("What does the text say about the repair club?", ["It asks visitors to pay a fixed price.", "It cannot guarantee to fix every object.", "It only repairs electrical equipment.", "It makes visitors bring their own materials."], "It cannot guarantee to fix every object.", "The text explicitly says nobody promised that every object could be repaired."),
            ("What impressed Daniel about fixing the lamp?", ["How much he learnt during the process.", "How quickly he could work without help.", "How easy it was to replace all the wires.", "How much money the volunteer earned."], "How much he learnt during the process.", "Daniel's greatest surprise was what he learnt by watching and asking questions."),
            ("Why does Daniel welcome visitors now?", ["He has already become an expert electrician.", "He dislikes working with other volunteers.", "The organiser recognised his communication skills.", "The club has stopped repairing clothes."], "The organiser recognised his communication skills.", "He was good at explaining things and meeting people, so this was a suitable volunteer role."),
            ("What is the writer's main purpose?", ["To explain how to replace a lamp switch.", "To argue that buying anything new is wrong.", "To compare the prices of different repair services.", "To show how joining a repair club changed Daniel's habits."], "To show how joining a repair club changed Daniel's habits.", "The text follows Daniel from throwing things away to learning repairs and helping others consider them."),
        ],
    ),
    _set(
        "reading-p4-podcast", 4, "Our first school podcast",
        "Five sentences have been removed. Choose A–H for gaps [1]–[5]. Three sentences are not needed.",
        """
Our English teacher asked us to create a school podcast about a local event. Our group chose the Saturday market, where people sold food, flowers and handmade gifts. None of us had recorded an interview before. [1] The teacher showed us how to use a phone to make a clear recording.

We wanted to speak to a baker, so we emailed her to arrange a visit. [2] This meant we could interview her before customers began arriving. We wrote some questions about her bread and how she had started her business.

When we reached the market, traffic on the nearby road was surprisingly loud. Our first recording included more car sounds than voices. [3] There we could hear the baker much better, although we still had to speak clearly.

The baker told us several interesting stories. We had planned a ten-minute podcast, but the interview alone lasted twenty minutes. [4] After listening to everything, we chose the clearest explanation and the funniest story.

Finally, we added a short introduction and some music that our class had made. We played the finished podcast to the class on Friday. [5] Hearing that made us feel that all our work had been useful.

A. She replied that we should come at eight, an hour before the market opened.
B. We therefore moved behind her stall, away from the busy road.
C. Several students said they wanted to visit the market after listening.
D. This was why we decided to ask for some advice before starting.
E. We had to remove some parts to keep the programme the right length.
F. Unfortunately, all the bread had been sold by the time we arrived.
G. We decided that a podcast about football would be easier to make.
H. Nobody in our group was allowed to bring a phone to school.
""",
        [
            ("Choose the sentence for gap [1].", list("ABCDEFGH"), "D", "'This' refers to their lack of interview experience; asking for advice leads naturally to the teacher's demonstration."),
            ("Choose the sentence for gap [2].", list("ABCDEFGH"), "A", "The baker's reply gives the early appointment time, explaining why they could talk before customers arrived."),
            ("Choose the sentence for gap [3].", list("ABCDEFGH"), "B", "Moving away from the noisy road solves the sound problem, and 'There' then refers to the new position."),
            ("Choose the sentence for gap [4].", list("ABCDEFGH"), "E", "A twenty-minute interview is too long for a ten-minute podcast, so they need to cut parts before choosing the best material."),
            ("Choose the sentence for gap [5].", list("ABCDEFGH"), "C", "The students' positive response explains what the group heard and why they felt their work was useful."),
        ],
    ),
    _set(
        "reading-p4-trail", 4, "Finding a better path",
        "Five sentences have been removed. Choose A–H for gaps [1]–[5]. Three sentences are not needed.",
        """
Last spring, our walking club planned to improve a path through the woods near our town. It was a beautiful route, but rain had damaged parts of it. [1] Because of these problems, some families had stopped using it.

Before beginning any work, we invited a park officer to walk along the route with us. [2] After her visit, we agreed to use only natural materials and to avoid a small area where birds were nesting.

Our first job was to clear fallen branches. Some were too heavy for one person to move safely. [3] Working together made the job quicker as well as safer. We piled the wood away from the path so insects could still live in it.

Next, we put small stones on the wettest part of the path. We wanted to know if the surface would stay firm. [4] When we returned, there were no large puddles and the stones were still in place.

We finished by adding a sign at the start of the route. It showed the distance and places where walkers could rest. On the opening day, a family with young children was the first to try the path. [5] We were delighted that the route could be enjoyed by more people again.

A. She explained how to protect the wildlife while repairing the path.
B. We decided to remove every tree beside the route.
C. Their parents said it was much easier to walk there than before.
D. In two places, deep mud made walking difficult.
E. So we waited until after the next rainy day to check our work.
F. For that reason, we carried the largest ones in pairs.
G. Nobody remembered to bring a map for the mountain climb.
H. We closed the new path permanently the following morning.
""",
        [
            ("Choose the sentence for gap [1].", list("ABCDEFGH"), "D", "The deep mud is a specific rain-related problem; 'these problems' in the next sentence refers to it and the damage."),
            ("Choose the sentence for gap [2].", list("ABCDEFGH"), "A", "The officer's advice explains the later decisions about natural materials and nesting birds."),
            ("Choose the sentence for gap [3].", list("ABCDEFGH"), "F", "'The largest ones' refers to heavy branches, and carrying them in pairs connects to 'Working together'."),
            ("Choose the sentence for gap [4].", list("ABCDEFGH"), "E", "Checking after rain tests whether the repaired surface stays firm; the next sentence reports the result."),
            ("Choose the sentence for gap [5].", list("ABCDEFGH"), "C", "'Their parents' refers to the family, whose positive reaction explains why the volunteers were delighted."),
        ],
    ),
    _set(
        "reading-p5-night-market", 5, "A night market",
        "Choose the correct word for each gap [1]–[6]. Each question has four choices.",
        """
Last month, my town organised its first night market. It took [1] in the main square on a warm Friday evening. Local shops stayed open late, and musicians played beside the fountain. There was a wide [2] of food, from fresh soup to homemade cakes.

My sister and I [3] to go by bike because we knew parking would be difficult. We arrived early and helped a neighbour set [4] her stall. She sells bags made from old curtains, so each one looks different.

By eight o'clock, the square was full of people. Everyone seemed to be in a good [5]. We stayed until the musicians finished, and I bought a small gift for a friend. The market was such a [6] that the organisers have already planned another one.
""",
        [
            ("Choose the word for gap [1].", ["place", "part", "care", "turn"], "place", "'Take place' means happen; the market took place in the square."),
            ("Choose the word for gap [2].", ["number", "choice", "piece", "amount"], "choice", "A 'wide choice of food' means many different kinds were available. 'A wide number' is not a natural expression."),
            ("Choose the word for gap [3].", ["decided", "suggested", "enjoyed", "avoided"], "decided", "'Decide' is followed by 'to' plus an infinitive: decided to go."),
            ("Choose the word for gap [4].", ["off", "out", "up", "away"], "up", "To 'set up a stall' means prepare it for use."),
            ("Choose the word for gap [5].", ["habit", "mood", "idea", "view"], "mood", "The phrase 'in a good mood' describes feeling happy."),
            ("Choose the word for gap [6].", ["success", "progress", "result", "effect"], "success", "An event can be 'such a success' when it goes very well."),
        ],
    ),
    _set(
        "reading-p5-community-run", 5, "A run for everyone",
        "Choose the correct word for each gap [1]–[6]. Each question has four choices.",
        """
I used to think running clubs were only for fast athletes. Then a friend told me about a group that meets in the park every Sunday. People of all ages take [1], and nobody has to run the whole route.

At my first session, a volunteer gave me some useful [2] about starting slowly. She explained that it is better to [3] a break than to become too tired. I walked for a while, then ran again when I felt ready.

The other runners were very friendly. One man offered to [4] me company near the end, when most people had gone ahead. By the time we finished, I was tired but proud of myself.

Since then, I have made steady [5]. I still do not worry about my speed. For me, the most important thing is to [6] time outdoors with other people.
""",
        [
            ("Choose the word for gap [1].", ["place", "part", "care", "charge"], "part", "'Take part' means participate in an activity."),
            ("Choose the word for gap [2].", ["advice", "opinion", "suggestion", "message"], "advice", "'Some useful advice' is natural. Advice is uncountable, whereas the other singular nouns would require a determiner such as 'a'."),
            ("Choose the word for gap [3].", ["make", "do", "take", "put"], "take", "The usual expression is 'take a break'."),
            ("Choose the word for gap [4].", ["hold", "stay", "keep", "bring"], "keep", "'Keep someone company' means stay with them so they are not alone."),
            ("Choose the word for gap [5].", ["progress", "success", "advantage", "distance"], "progress", "'Make steady progress' means improve gradually over time."),
            ("Choose the word for gap [6].", ["pass", "spend", "cost", "pay"], "spend", "'Spend time' describes using time for an activity."),
        ],
    ),
    _set(
        "reading-p6-book-club", 6, "Our lunchtime book club",
        "Write ONE word in each gap [1]–[6]. Spelling matters; answers are checked without regard to capital letters.",
        """
Our school book club started three months [1]. We meet every Thursday at lunchtime in a quiet room next [2] the library. You do not have to buy the books because you can borrow them from school.

At our first meeting, we chose a short adventure story [3] was set on an island. Most people enjoyed it, although a few thought the ending was too easy to guess. We talked about [4] character we liked best and explained our choices.

There are twelve members now, and all [5] us have different tastes. That makes our discussions interesting. If you would like to join, please send [6] email to Mrs Lewis before Wednesday.
""",
        [
            ("Write one word for gap [1].", [], "ago", "Use 'ago' after a length of time to say how long before now something happened."),
            ("Write one word for gap [2].", [], "to", "The fixed phrase is 'next to', meaning beside."),
            ("Write one word for gap [3].", [], "which", "A defining relative clause describes the story; 'which' or 'that' can refer to a thing.", ["which", "that"]),
            ("Write one word for gap [4].", [], "which", "'Which character' asks for a choice among the characters; 'what character' is also grammatically acceptable here.", ["which", "what"]),
            ("Write one word for gap [5].", [], "of", "Use 'all of us' before an object pronoun to mean everyone in the group."),
            ("Write one word for gap [6].", [], "an", "Use 'an' before 'email', which starts with a vowel sound."),
        ],
    ),
    _set(
        "reading-p6-hostel", 6, "A useful place to stay",
        "Write ONE word in each gap [1]–[6]. Spelling matters; answers are checked without regard to capital letters.",
        """
Dear Sam,

I have just returned from a weekend at Lake House Hostel. It is smaller [1] the hotel we stayed in last year, but much friendlier. The owners have lived in the village [2] 2015 and know all the best walks.

Every morning, they prepare breakfast for their guests. There is also a kitchen [3] you can cook your own evening meal. I brought pasta, so I did not need [4] eat in a restaurant.

You should book early if you want to go [5] the summer. The hostel is popular, but it is not [6] expensive as the big hotels nearby. I think you would like it!

Best wishes,
Robin
""",
        [
            ("Write one word for gap [1].", [], "than", "A comparative adjective such as 'smaller' is followed by 'than' when comparing two things."),
            ("Write one word for gap [2].", [], "since", "Use 'since' with the present perfect and a starting point in time: since 2015."),
            ("Write one word for gap [3].", [], "where", "'Where' introduces a relative clause describing what you can do in the kitchen."),
            ("Write one word for gap [4].", [], "to", "The negative form 'did not need' is followed by 'to' and an infinitive."),
            ("Write one word for gap [5].", [], "in", "Use 'in' with a season: in the summer. 'During' is also grammatical.", ["in", "during"]),
            ("Write one word for gap [6].", [], "as", "Use 'not as + adjective + as' to compare two things. 'Not so expensive as' is also grammatical.", ["as", "so"]),
        ],
    ),
]
