"use client";
import { useState } from "react";
import SideBar from "../components/SideBar";
import { useSearchParams } from "next/navigation";

const Home = () => {
	const chatId = useSearchParams().get('id');
	const [sideBar, setSideBar] = useState(false);
	const [showSettings, setShowSettings] = useState(false);
	const [prompt, setPrompt] = useState("");
	const myChats = [
		{
			_id: 1,
			title: "1. Random thoughts about cosmic microwaves",
			chats: ["Yo", "What's up?", "Got any memes?", "Nah but I've got chaotic energy.", "kol", "kolakdn", "verify"]
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
	const currChat = myChats.find(chat => chat._id.toString() === chatId)?.["chats"];

	const handlePrompt = async () => {
		if (!prompt) return;

		const response = await fetch('/api/prompt', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ prompt }),
		});
		const res = await response.json();

		//Implement chat, db update logic here
		if (currChat) {
			//
		}else {
			//
		}
		setPrompt("");
	}
	return (
		<div className="h-screen w-screen flex flex-col">
			<SideBar sideBar={sideBar} setSideBar={setSideBar} showSettings={showSettings} setShowSettings={setShowSettings} />
			{sideBar && <div className='h-full w-full absolute z-5 top-0 bg-[#a5a5a514]' onClick={() => setSideBar(false)}></div>}
			{showSettings &&
				<div>
					<div className='w-70 bg-[#444444f3] rounded-2xl p-2 bottom-18 left-2.5 z-30 absolute'>
						<p className='p-2 cursor-pointer hover:bg-[#81818146] rounded-xl z-40'>Documents</p>
						<p className='p-2 cursor-pointer hover:bg-[#81818146] rounded-xl z-40'>Settings</p>
						<p className='p-2 cursor-pointer hover:bg-[#81818146] rounded-xl z-40'>Log out</p>
					</div>
					<div className='h-full w-full absolute z-10 top-0' onClick={() => setShowSettings(false)}></div>
				</div>}
			<div className='flex fixed top-0 w-full items-center gap-4 p-2'>
				<img src="menu.svg" alt="menu" className="w-7 invert cursor-pointer box-content p-1 hover:bg-[#81818146] rounded-xl" onClick={() => { setSideBar(!sideBar) }} />
				<span className="text-2xl font-semibold">Cred Saathi</span>
			</div>
			<main className={`mt-14 mb-24 h-full w-full flex flex-col items-center overflow-x-hidden ${currChat ? 'justify-between' : 'justify-center'}`}>
				<div className={`flex w-full flex-col items-center justify-center gap-4 ${currChat ? 'p-16' : 'mb-5'}`}>
					{currChat ? (
						currChat.map((msg, i) => {
							if (i % 2) return (
								<div
									key={i}
									className="mb-4 p-4 bg-[#303030] rounded-2xl w-2/3 shadow-lg self-start"
								>
									{msg}
								</div>
							)
							else return (
								<div
									key={i}
									className="mb-4 p-4 bg-emerald-500 rounded-2xl w-1/3 shadow-lg self-end" >
									{msg}
								</div>
							)
						})
					) :
						<h1 className='text-4xl p-7'>Hello Jee!</h1>}
				</div>
				<div className={`w-[102vw] bg-[#00031e81] h-24 fixed -bottom-1 backdrop-blur-xs blur-xs ${!currChat && 'hidden'}`}></div>
				<div className={`w-2/3 ${currChat && 'fixed'} bottom-6 bg-[#303030] flex justify-between items-center rounded-4xl shadow-lg`}>
					<img src="plus.svg" alt="add" className='size-10 p-2 bg-green-500 rounded-full ml-3 cursor-pointer' />
					<input
						type="text"
						placeholder='Ask anything'
						value={prompt}
						onChange={(e) => setPrompt(e.target.value)}
						className='w-1/1 h-1/1 p-4 text-white focus:outline-none'
						onKeyDown={(e) => {
							if (prompt && e.key == "Enter") handlePrompt()
						}} />
					<img
						src="arrowUp.svg"
						onClick={handlePrompt}
						className='size-10 p-2 bg-green-500 rounded-full mr-3 cursor-pointer' />
				</div>
			</main>
		</div>
	)
}

export default Home