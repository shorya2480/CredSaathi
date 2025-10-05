import { useState } from 'react'
import './loginPage.css'
import { FiEye, FiEyeOff } from "react-icons/fi";

const loginPage = () => {
    const [showPass, setShowPassword] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (btn) => {
        console.log(email, password);
        setEmail('');
        setPassword('');
        btn.disabled = true;
    }
    return (
        <div>
            <div className='flex flex-col justify-center items-center h-screen gap-6'>
                <h1 className='font-semibold text-3xl'>Cred Saathi</h1>
                <h1 className='text-4xl'>Log in or sign up</h1>

                <input id='email' type="email" value={email} className='w-[340px] border border-gray-300 rounded-4xl p-4' placeholder='Email address' onChange={val => setEmail(val.target.value)} />

                <div id='passBox' className='flex items-center w-[340px] border border-gray-300 rounded-4xl'>
                    <input id='pass' type={showPass ? "text" : "password"} value={password} className='w-1/1 p-4 border-0' placeholder='Password' onChange={val => setPassword(val.target.value)} />

                    <div className='flex items-center justify-center cursor-pointer border-gray-300 h-full mr-1' onClick={() => setShowPassword(!showPass)}>
                        {(showPass) ? <FiEyeOff className='size-full p-2' /> : <FiEye className='size-full p-2' onClick={() => setShowPassword(!showPass)} />}
                    </div>

                </div>
                <button className='w-[340px] p-4 bg-gray-950 text-white cursor-pointer rounded-4xl' onClick={(e) => handleSubmit(e.target)}>Continue</button>
            </div>
        </div>
    )
}

export default loginPage
