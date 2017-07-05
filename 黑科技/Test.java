public class Test {
	
	#ifdef _MYCRO
	public static String funcabc(){
		return "yourabc";
	}
	#endif
	
	#ifdef _YOURCRO
	public static String funcabc(){
		return "myabc";
	}
	#endif
	
	public static void main(String[] args){
	#ifdef _MYCRO
        String mycro = "abc";
        #endif
        #ifdef _YOURCRO
        String mycro = "bcd";
        #endif
	System.out.print(mycro);
        System.out.println(Test.funcabc());
	}
}
