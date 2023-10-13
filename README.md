# CS2 build-number dumper

Dumps engine build number from the engine dll for CS2.

## Usage

```
python main.py engine2.dll
```

### Output

```
> python main.py engine2.dll
searching for: b'2023\x00'.
found at engine2.dll!0x00000000003FC0F7: 'Oct  5 2023' -> build 9842
```

## What is build number

Build number determines the version (or rather build) of the game. It can be used to distinguish between different game versions.

The build number function that Valve uses for generation is just a day counter since *October 24 1994*. This is the date that Half-Life was first released.

## Original function

Fun fact, the function that is used in CS2 for generating the build number is the same as in GoldSrc, so the function is from 1996. This may probably be the oldest code in the entire CS2 engine.

This function was actually different in CSGO however, I think that valve decided to replace it with the old function just for fun.

```c++
// char *date = "Oct 24 1996";
char *date = __DATE__ ;

char *mon[12] = 
{ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
char mond[12] = 
{ 31,    28,    31,    30,    31,    30,    31,    31,    30,    31,    30,    31 };

// returns days since Oct 24 1996
int build_number( void )
{
	int m = 0; 
	int d = 0;
	int y = 0;
	static int b = 0;

	if (b != 0)
		return b;

	for (m = 0; m < 11; m++)
	{
		if ( Q_strnicmp( &date[0], mon[m], 3 ) == 0 )
			break;
		d += mond[m];
	}

	d += atoi( &date[4] ) - 1;

	y = atoi( &date[7] ) - 1900;

	b = d + (int)((y - 1) * 365.25);

	if (((y % 4) == 0) && m > 1)
	{
		b += 1;
	}

	b -= 34995; // Oct 24 1996

	return b;
}
```