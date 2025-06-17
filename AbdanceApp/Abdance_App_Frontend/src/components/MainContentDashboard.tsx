import { ReactNode } from "react"

type Props = {
    children: ReactNode;
}

export default function MainContentDashboard({children}: Props) {
    return (
        <div className="md:bg-[#ebdaff] md:text-[#200045] w-full bg-[#2b005d58] rounded-3xl ">
            {children}
        </div>
    )
}