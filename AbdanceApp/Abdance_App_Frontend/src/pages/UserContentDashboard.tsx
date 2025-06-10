import { ReactNode } from 'react';
import {UserTable} from '../components'




interface Props{
    children?: ReactNode;
}

export const UserContentDashboard = ({children}: Props) =>{
    return (
        <>
            <h1>USUARIOS</h1>
            <UserTable />
        </>
    )
}
export default UserContentDashboard;

