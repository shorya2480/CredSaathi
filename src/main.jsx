import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Login from './loginPage.jsx'
import FileNotFound from './FileNotFound.jsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
  {path: "/", element: <App /> },
  {path: "/login", element: <Login/> },
  {path: "*", element: <FileNotFound/> },
]);

createRoot(document.getElementById('root')).render(
    <div>
      <RouterProvider router={router} />
    </div>
)
