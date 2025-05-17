

const Background = () => {
  return ( 
    <div className="fixed inset-0 -z-50 w-full h-full overflow-hidden">
      <picture  className="w-full h-full block">
          <source media="(max-width: 639px)" srcSet="/BackGround-mobile.png" />
          <img 
            src="/BackGround.png" 
            alt="Background"
            className="w-full h-full object-cover object-center"
            loading="eager"
          />
        </picture>
      </div>
  );
};

export default Background;