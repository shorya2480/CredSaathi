"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

const SideBar = ({ sideBar, setSideBar, showSettings, setShowSettings }) => {
  const router = useRouter();

  const [showChats, setShowChats] = useState(false);
  const currUser = {
    user: "hriddhiman@xyz.com",
    dp: "/logo2.jpg",
    name: "Hriddhiman"
  }
  const myChats = [
    {
      _id: 1,
      title: "1. Random thoughts about cosmic microwaves",
      chats: ["Yo", "What's up?", "Got any memes?", "Nah but I've got chaotic energy."]
    },
    {
      _id: 2,
      title: "2. Why is my cereal judging me?",
      chats: ["Sup", "Need something?", "Explain recursion?", "It's functions eating themselves. Happy now?"]
    },
    {
      _id: 3,
      title: "3. The existential crisis of a left shoe",
      chats: ["Hey", "What now?", "How do I get smarter?", "Read stuff. Shocking, I know."]
    },
    {
      _id: 4,
      title: "4. My WiFi has emotional damage",
      chats: ["Hi", "Yeah?", "Tell me something random", "Bananas are berries. You're welcome."]
    },
    {
      _id: 5,
      title: "5. A dissertation on why pens disappear",
      chats: ["Hello", "What’s good?", "Got advice?", "Don’t run your code at 3 AM."]
    },
    {
      _id: 6,
      title: "6. Time is fake and so is my motivation",
      chats: ["Yo", "Need help?", "Explain arrays", "They hold stuff. Boom."]
    },
    {
      _id: 7,
      title: "7. The tragedy of a lukewarm pizza slice",
      chats: ["Hey", "Speak", "Tell me a fact", "Octopuses have three hearts."]
    },
    {
      _id: 8,
      title: "8. Why does my brain buffer like a bad video?",
      chats: ["Hi", "Listening", "Give me wisdom", "Touch grass occasionally."]
    },
    {
      _id: 9,
      title: "9. A philosophical rant about socks",
      chats: ["Yo", "Go ahead", "Is AI scary?", "Only when you write spaghetti code."]
    },
    {
      _id: 10,
      title: "10. A saga about losing my charger again",
      chats: ["Sup", "Mm?", "Make me laugh", "Your compiler errors did that."]
    },
    {
      _id: 11,
      title: "11. The lore behind my unfinished assignments",
      chats: ["Hello", "Huh?", "Teach me JS", "Start by not crying over it."]
    },
    {
      _id: 12,
      title: "12. Things I say to avoid real responsibilities",
      chats: ["Hey", "Yes?", "Why am I like this?", "Honestly? Same."]
    }
  ];

  const Btn = ({ icon, imgWidth = 6, text, clickHandler }) => {
    return (
      <div className="flex gap-2 p-2 cursor-pointer items-center hover:bg-[#81818146] rounded-xl" onClick={clickHandler}>
        <img src={icon} alt={text} className={`invert w-${imgWidth}`} />
        {text && <p>{text}</p>}
      </div>
    )
  }

  return (
    <div className={`flex flex-col fixed top-0 h-full w-75 bg-[#181818] text-white transform transition-transform duration-300 z-10 overflow-y-auto ${sideBar ? '' : '-translate-x-full'}`}>
      <div className="sticky top-0 flex gap-4 z-20 p-4 py-2 items-center">
        <div className="flex gap-4 w-full items-center">
          <img src='logo2.jpg' className="cursor-pointer size-6 rounded-sm" alt="logo" onClick={() => { router.push('/home'), setSideBar(false) }} />
          <div className="text-xl font-bold">Cred Saathi</div>
        </div>
        <img src="sidebar.svg" alt="close" className="w-5 invert cursor-ew-resize box-content p-2 hover:bg-[#81818146] rounded-xl" onClick={() => { setSideBar(!sideBar) }} />
      </div>

      <div className='mr-1 h-full flex flex-col justify-between transform transition-transform duration-300 ease-in-out'>
        <div className='h-full overflow-y-auto p-2'>
          <Btn icon={'pencil.svg'} text={'New Chat'} 
          clickHandler={() => {router.push('/home'), setSideBar(false)} } />
          <Btn icon={'search.svg'} imgWidth={5} text={'Search Chats'} />

          <div className='p-1 px-2 flex items-center cursor-pointer gap-2 mt-4 w-full text-[#afafaf]' onClick={() => setShowChats(!showChats)}>
            <p>Your Chats</p>
            <img src="greaterthan.svg" className={`size-4 invert transition-transform ${showChats ? 'rotate-90' : ''}`} />
          </div>

          <div className={`flex flex-col max-h-60 ${showChats ? 'block' : 'hidden'}`}>
            <hr className='border-gray-700 my-2' />
            {myChats ? (
              myChats.map((prompt) => (
                <div
                  key={prompt._id}
                  onClick={() => {
                    router.push(`/home?id=${prompt._id}`)
                    setSideBar(false);
                  }}>
                  <p className="truncate p-2 cursor-pointer hover:bg-[#81818146] rounded-xl">{prompt.title}</p>
                </div>
              ))
            ) : (
              <p>Ask Cred Saathi to look up for chats</p>
            )}
          </div>
        </div>
      </div>

      <hr className='border-gray-700 mb-2' />

      <div className='flex items-center cursor-pointer gap-2 p-2 hover:bg-[#81818146] rounded-xl z-40 m-2 mt-0' onClick={() => setShowSettings(!showSettings)}>
        <img src={currUser.dp} alt="dp" className='w-6 rounded-full' />
        <p>{currUser.name}</p>
      </div>
    </div>
  )
}

export default SideBar