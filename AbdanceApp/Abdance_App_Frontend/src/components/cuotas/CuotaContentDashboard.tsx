import { ReactNode } from 'react';
import { CuotaTable } from '../CuotaTable';

interface Props{
    children?: ReactNode;
}

export const CuotaContentDashboard = ({children}: Props) =>{
    return (
        <>
            <h1 className='tracking-wide text-4xl font-black text-gray-300 md:dark:text-gray-900'>CUOTAS</h1>
            <CuotaTable />
        </>
    )
}
export default CuotaContentDashboard;