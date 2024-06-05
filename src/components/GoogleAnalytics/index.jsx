import React from "react"
import {Script} from "gatsby";

const Analytics = ({}) => {
    return (
        <div>
            <Script async src="https://www.googletagmanager.com/gtag/js?id=G-RG76MK8WNZ"></Script>
            <Script id="gtag-config" strategy="off-main-thread" forward={[`gtag`]}>
                {`
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-RG76MK8WNZ');
        `}
            </Script>
        </div>
    )
}

export default Analytics
