
import { useEffect } from 'react';

export const useFavicon = (url: string) => {
    useEffect(() => {
        const link = document.querySelector("link[rel*='icon']") as HTMLLinkElement|| document.createElement('link') as HTMLLinkElement;
        link.rel = 'icon';
        link.href = url;
        document.head.appendChild(link);
        }, [url]);
    };