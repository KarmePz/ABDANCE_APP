
function parseDates(userData: any) {
    const toISO = (dateString?: string | null) => {
        if (!dateString) return null;
        const d = new Date(dateString);
        if (isNaN(d.getTime())) return null;
        return d.toISOString().replace("Z", "");//Se quita la Z
    };

    return {
        ...userData,
        fechaNacimiento: toISO(userData.fechaNacimiento),
        fechaInscripcion: toISO(userData.fechaInscripcion),
    };
}
export default parseDates;