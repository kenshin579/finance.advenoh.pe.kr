import React from "react"
import {Script} from "gatsby";

const Analytics = ({}) => {
    return (
        <div>
            <Script async src="https://www.googletagmanager.com/gtag/js?id=G-RG76MK8WNZ"></Script>
            <Script>
                {`
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-RG76MK8WNZ');
        `}
            </Script>
            <Script data-ad-client="ca-pub-8868959494983515" async
                    src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></Script>
        </div>
    )
}

export default Analytics
