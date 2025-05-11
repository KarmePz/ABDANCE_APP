

type Props = {
    name : string;
    type ?: string;
    placeholder ?: string;
    label ?: string;
}

function InputButton({name, type='text', placeholder, label}: Props) {

    return (
        <div className="relative z-100 flex justify-center items-center h-screen">
            <label>{label}</label>
            <input className='p-2 border border-gray-300 rounded w-full bg-gray-800 text-gray-200' 
                type = {type} 
                name={name} 
                placeholder={placeholder} >
            </input>
        </div>
    )
}

export default InputButton