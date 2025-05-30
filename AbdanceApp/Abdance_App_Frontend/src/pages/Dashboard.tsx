
import { ReactNode } from 'react';
import {Background, MainContentDashboard, SideBar} from '../components'
import { Outlet } from 'react-router-dom';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useFavicon } from '../hooks/useFavicon';


interface Props{
    children?: ReactNode;
}

export const Dashboard = ({children}: Props) =>{
    
    useDocumentTitle("ABDANCE Dashboard");
    useFavicon("/dance.ico")
    return (
        <>
        
            <Background />
            <div className='w-full flex justify-between p-4 bg-[#1f004d91]'>
                <img src="/Logo.png" className="h-12 md:h-16 max-w-[160px] object-cover" alt="logo" />
                <h1 className="text-white text-3xl p-2 ">alejandro buffa</h1>
            </div>
            <div className='flex flex-row gap-5'>
            <SideBar />
            <MainContentDashboard>
                <Outlet />
            </MainContentDashboard>
            
            
            </div>
            {/* Navbar rolUsuario{"Alumno"} */}
            {/* Main Content */}
            
        </>
    )
}
export default Dashboard;
