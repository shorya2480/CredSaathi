import { useEffect, useState } from 'react'
import './App.css'
import logo from '/logo2.jpg'
import { SlNote } from "react-icons/sl";
import { FaArrowUp } from "react-icons/fa";
import { IoMenu } from "react-icons/io5";
import { IoIosSearch } from "react-icons/io";
import { TbLayoutSidebar } from "react-icons/tb";
import { PiGreaterThan } from "react-icons/pi";
import { NavLink } from 'react-router-dom';

function App() {
  const [width, setWidth] = useState(window.innerWidth);
  const [showSideBar, setShowSideBar] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showChats, setShowChats] = useState(false);

  const db = {
    "hriddhiman@xyz.com": {
      dp: logo,
      name: "Hriddhiman",
      chats: {
        "chat1": [
          { from: "user", message: "Hello" },
          { from: "bot", message: "Hi there! How can I assist you today?" },
          { from: "user", message: "Can you tell me a joke?" },
          { from: "bot", message: "Sure! Why don't scientists trust atoms? Because they make up everything!" }
        ],
        "chat2": [],
        "chat3": []
      }
    }
  }
  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth);
    };

    window.addEventListener("resize", handleResize);
    if (width < 768 && showSideBar) toggleSidebar(), setShowSettings(false);
    return () => window.removeEventListener("resize", handleResize);
  }, [width]);

  const toggleSidebar = () => {
    const sidebar = document.querySelector('aside');
    sidebar.style.transition = 'transform 0.3s ease-in-out';
    sidebar.style.transform = showSideBar ? 'translateX(-100%)' : 'translateX(0)';
    sidebar.style.position = (width < 768 || showSideBar) ? 'absolute' : 'relative';
    setTimeout(() => {
      sidebar.style.transition = '';
    }, 300);

    setShowSideBar(!showSideBar);
  };

  return (
    <div className='flex bg-[#212121]'>
      {showSettings &&
        <div className='w-screen h-screen absolute z-10' onClick={() => setShowSettings(!showSettings)}></div>
      }
      <aside className='h-screen w-[280px] bg-[#181818] z-10 text-white p-2 flex flex-col justify-between'>
        <div className='flex items-center justify-between p-2 mb-4'>
          <NavLink to='/' onClick={() => toggleSidebar()}>
            <img src={logo} className="cursor-pointer w-6 rounded-sm" alt="logo" />
          </NavLink>

          <TbLayoutSidebar color='#aaaaaa' className='btn p-2 box-content size-6 cursor-pointer' onClick={() => toggleSidebar()} />
        </div>

        <div id='scrollBox' className='h-1/1 overflow-y-auto'>

          <div className='btn p-2 flex items-center cursor-pointer gap-2'>
            <SlNote className='size-4' />
            <p>New Chat</p>
          </div>

          <div className='btn p-2 flex items-center cursor-pointer gap-2'>
            <IoIosSearch className='size-5' />
            <p>Search Chats</p>
          </div>

          <div className='p-2 flex items-center cursor-pointer gap-2 mt-4' onClick={() => setShowChats(!showChats)}>
            <p>Chats</p>
            <PiGreaterThan className={`mt-1 size-3 transition-transform ${showChats ? 'rotate-90' : ''}`} />
          </div>

          <div className={`flex flex-col gap-2 max-h-60 ${showChats ? 'block' : 'hidden'}`}>
            <hr className='border-gray-700 my-2' />
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 1</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 2</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 3</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 4</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 5</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 6</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 7</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 8</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 9</p>
            </NavLink>
            <NavLink to='/' className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => alert('feature coming soon!')}>
              <p>Chat 10</p>
            </NavLink>
          </div>
        </div>
        <div>
          {showSettings &&
            <div className='w-[90%] bg-[#444444f3] rounded-2xl p-2 bottom-16 z-30 absolute'>
              <p className='btn z-40 p-2 cursor-pointer'>Settings</p>
              <p className='btn z-40 p-2 cursor-pointer'>Log out</p>
            </div>
          }
          <hr className='border-gray-700 my-2' />
          <div className='btn p-2 flex items-center cursor-pointer gap-2' onClick={() => setShowSettings(!showSettings)}>
            <img src={db['hriddhiman@xyz.com'].dp} alt="dp" className='w-6 rounded-full' />
            <p>{db['hriddhiman@xyz.com'].name}</p>
          </div>
        </div>
      </aside>

      {(width < 768 && showSideBar) &&
        <div className='w-screen h-screen absolute bg-[#1616168d]' onClick={() => toggleSidebar()}></div>
      }

      <main className='h-screen w-full text-white'>
        <div className='flex  items-center text-2xl font-semibold gap-4 mt-3 absolute'>
          {!(width > 768 && showSideBar) &&
            <IoMenu onClick={() => toggleSidebar()} className='btn p-1 box-content size-8 m-2 cursor-pointer' />
          }
          <span className='m-2'>Cred Saathi</span>
        </div>

        <div className='flex h-90/100 flex-col items-center justify-center'>
          <h1 className='text-4xl p-7'>Hello Jee!</h1>
          <div className='w-2/3 bg-[#303030] flex justify-between items-center rounded-4xl shadow-xl'>
            <input className='w-1/1 h-1/1 p-4 text-white focus:outline-none' type="text" placeholder='Ask anything' />
            <FaArrowUp onClick={() => alert("Feature coming soon!")} className='w-8 h-8 p-[5px] bg-green-500 rounded-full mr-3 cursor-pointer' />
          </div>
        </div>

      </main>
    </div>
  )
}

export default App
