import { NavLink } from 'react-router-dom';
import logo from '/logo2.jpg'

const fileNotFound = () => {
  return (
    <div className='w-screen h-screen flex flex-col justify-center items-center bg-[#212121] text-white text-center p-4 gap-4'>
      <h1 className='text-7xl'>404</h1>
      <p className='text-3xl'>File not found</p>
      <p>The site configured at this address does not contain the requested file.</p>
      <p>If this is your site, make sure that the filename case matches the URL as well as any file permissions.</p>
      <p>For root URLs (like <code>http://example.com/</code>) you must provide an index.html file.</p>

      <NavLink to="/">
        <img src= {logo} alt="Cred Saathi" className='rounded-full size-15' />
      </NavLink>
    </div>
  )
}

export default fileNotFound
